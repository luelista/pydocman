from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from dropmefiles.models import Clipboard, Item, Favorites
from thewiki.models import User


class LoginCheckMiddleware(object):
    def process_request(self, request):
        request.member = None
        if request.session.get('member_id', None) != None:
            request.member = User.objects.get(pk=request.session['member_id'])



def session_info_context(request):
    login = False
    favs = None
    if request.member != None:
        favs = Favorites.objects.filter(user=request.member)
        login = True
    return {
        "loginUser": request.member,
        "login": login,
        "favs": favs
    }

