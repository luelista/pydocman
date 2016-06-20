from wsgiref.util import FileWrapper

import os

from actstream import action
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sessions.backends import file
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect

from actstream.models import user_stream, following

from dropme.forms import CreateClipboardForm
from dropme.models import Clipboard, UserPermission, Document
from dropme import helper
from dropme.serializers import UserSerializer, ClipboardSerializer, DocumentSerializer
from rest_framework import viewsets


@login_required
def myprofile(request):
    events = request.user.actor_actions.all()
    return render(request, "dropme/userprofile.html", {
        "user": request.user,
        "clipboards": request.user.clipboard_set.all(),
        "events": events
    })

@login_required
def userprofile(request):
    events = request.user.actor_actions.all()
    user_clipboards = request.user.clipboard_set.filter(state__neq=Clipboard.STATE_PRIVATE, listable=1)
    return render(request, "dropme/userprofile.html", {
        "user": request.user,
        "clipboards": user_clipboards,
        "events": events
    })

@login_required
def dashboard(request):
    events = user_stream(request.user, with_user_activity=True)
    cbs = following(request.user, Clipboard)
    return render(request, "dropme/dashboard.html", {
        "events": events,
        "following_clipboards": cbs
    })

def homepage(request):
    if request.user.is_authenticated() and not 'no_redirect' in request.GET:
        return redirect(dashboard)
    else:
        return render(request, "dropme/homepage.html", {})

@login_required
def create_clipboard(request):
    if request.method == 'POST':
        form = CreateClipboardForm(session_user=request.user, data=request.POST)
        if form.is_valid():
            cb = Clipboard(title = form.cleaned_data['title'],
                           created_by = request.user)

            if form.cleaned_data['permission_preset'] == 'private':
                cb.allow_public_view = False
                cb.allow_public_add_documents = False
            elif form.cleaned_data['permission_preset'] == 'protected':
                cb.allow_public_view = True
                cb.allow_public_add_documents = False
            elif form.cleaned_data['permission_preset'] == 'inbox':
                cb.allow_public_view = False
                cb.allow_public_add_documents = True
            cb.save()

            UserPermission.objects.create(for_user=request.user, clipboard=cb,
                                          allow_view=True, allow_add_documents=True, allow_change=True)
            action.send(request.user, verb='created a new clipboard', target=cb)

            return HttpResponseRedirect(reverse('show_clipboard', kwargs=cb.get_url_args()))
    else:
        form = CreateClipboardForm(session_user=request.user)

    return render(request, 'dropme/create_clipboard.html', {'form': form})


def show_clipboard(request, token, slug=None):
    cb = Clipboard.objects.get(token=token)
    if not cb.has_view_permission(request.user):
        raise PermissionDenied
    items = cb.document_set.filter(deleted_at__isnull=True).order_by('-created_at')
    return render(request, 'dropme/show_clipboard.html', { 'cb': cb, 'docs': items })


def show_document(request, doc_id):
    doc = Document.objects.get(id=doc_id)
    cb = doc.clipboard
    if not cb.has_view_permission(request.user):
        raise PermissionDenied
    if doc.deleted_at and not cb.has_change_permission(request.user):
        raise PermissionDenied
    return render(request, 'dropme/show_document.html', { 'doc': doc })


def file_preview(request, doc_id, size, page=1):
    doc = Document.objects.get(id=doc_id)
    cb = doc.clipboard
    if not cb.has_view_permission(request.user):
        raise PermissionDenied
    if doc.deleted_at and not cb.has_change_permission(request.user):
        raise PermissionDenied
    """
    Send a file through Django without loading the whole file into
    memory at once. The FileWrapper will turn the file object into an
    iterator for chunks of 8KB.
    """
    if size == 'thumb':
        filename = doc.get_thumb_filespec(page)
    elif size == 'page':
        filename = doc.get_page_preview_filespec(page)
    else:
        raise FileNotFoundError("size parameter must be 'page' or 'thumb'")
    wrapper = FileWrapper(open(filename, 'rb'))
    response = HttpResponse(wrapper, content_type='text/plain')
    response['Content-Length'] = os.path.getsize(filename)
    return response


def file_raw(request, token, slug=None):
    return render(request, 'dropme/show_document.html', {  })


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class ClipboardViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Clipboard.objects.all()
    serializer_class = ClipboardSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

