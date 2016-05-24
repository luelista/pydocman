from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect

from actstream.models import user_stream, following

from dropme.forms import CreateClipboardForm
from dropme.models import Clipboard, UserPermission
from dropme import helper

@login_required
def myprofile(request):
    events = request.user.actor_actions.all()
    return render(request, "dropme/userprofile.html", {
        "user": request.user,
        "clipboards": request.user.clipboard_set,
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

            return HttpResponseRedirect(reverse('show_clipboard', kwargs=cb.get_url_args()))
    else:
        form = CreateClipboardForm(session_user=request.user)

    return render(request, 'dropme/create_clipboard.html', {'form': form})


def show_clipboard(request, token, slug=None):
    cb = Clipboard.objects.get(token=token)
    if not cb.has_view_permission(request.user):
        raise PermissionDenied
    return render(request, 'dropme/show_clipboard.html', { 'cb': cb })


def show_document(request, token, slug=None):
    return render(request, 'dropme/show_document.html', {  })


def file_preview(request, token, slug=None):
    return render(request, 'dropme/show_document.html', {  })


def file_raw(request, token, slug=None):
    return render(request, 'dropme/show_document.html', {  })

