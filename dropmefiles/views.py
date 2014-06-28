from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.exceptions import PermissionDenied
from django.utils.safestring import mark_safe
from dropmefiles.models import Clipboard, Item, Favorites, Events
from thewiki.models import User, Userlink
from django.shortcuts import get_object_or_404

from pygments.lexers import guess_lexer_for_filename, get_lexer_by_name

from pygments import highlight
from pygments.formatters import HtmlFormatter


# Create your views here.
def index(request):
    events = None
    if request.member != None:
        contacts = Userlink.objects.contact_names(request.member)
        events = Events.objects.filter(user_id__in=contacts).order_by('-created')[:20]
    return render(request, "dropmefiles/testindex.html", {"events": events})

def list_clipboards(request):
    if request.session.get('member_id', None) != None:
        user = request.member
        #ser.objects.get(id=request.session['member_id'])
        
        list = Clipboard.objects.filter(owner=user.username)
        return render(request, "dropmefiles/clipboard_list.html", { "list": list })
    else:
        return render(request, "dropmefiles/not_logged_in.html")

def show_clipboard(request, owner, cbname):
    try:
        clipboard = Clipboard.objects.get(name=cbname, owner_id=owner)
        if not clipboard.view_perm_of(request.member):
            raise PermissionDenied("Forbidden to load private clipboard")
        cbitems = Item.objects.filter(clipboard=clipboard)
        return render(request, "dropmefiles/thumbview.html", { "clipboard": clipboard, "items": cbitems })
    except Clipboard.DoesNotExist:
        raise Http404("Clipboard not found")

def show_item(request, owner, cbname, filename):
    item = get_object_or_404(Item, clipboard__name=cbname, clipboard__owner_id=owner, url_filename=filename)
    if not item.clipboard.view_perm_of(request.member):
            raise PermissionDenied("Forbidden to load private clipboard")
    
    formatted = None
    if item.filetype == "text" or item.filetype == "code":
        code = item.read_file_contents()
        try:
            lexer = guess_lexer_for_filename(item.filename, code)
        except:
            lexer = get_lexer_by_name("php")
        htmlformatter = HtmlFormatter(linenos=True, cssclass="source")
        formatted = mark_safe(highlight(code, lexer, htmlformatter))
    
    return render(request, "dropmefiles/itemview.html", { "item": item, "formattedCode": formatted })

def show_user(request, username):
    user = get_object_or_404(User, username=username)
    clipboards = Clipboard.objects.filter(owner=user)
    if user != request.member:
        clipboards = clipboards.filter(state=Clipboard.STATE_PROTECTED)
    return render(request, "dropmefiles/userview.html", { "user": user, "clipboards": clipboards })

def show_raw_item(request, owner, cbname, filename):
    item = get_object_or_404(Item, clipboard__name=cbname, clipboard__owner_id=owner, url_filename=filename)
    if not item.clipboard.view_perm_of(request.member):
            raise PermissionDenied("Forbidden to load private clipboard")
    response = HttpResponse("Success")
    response["X-Accel-Redirect"] = "/protected_files" + item.server_filespec
    del response["Content-Type"]
    return response


def login(request):
    if request.POST:
        m = User.objects.get(username=request.POST['username'])
        if m.check_password(request.POST['password']):
            request.session['member_id'] = m.id
            #return HttpResponse("You're logged in.")
            return HttpResponseRedirect("/")
        else:
            return HttpResponse("Your username and password didn't match.")
    else:
        return render(request, "dropmefiles/login.html")

#...And this one logs a member out, according to login() above:

def logout(request):
    try:
        del request.session['member_id']
    except KeyError:
        pass
    return HttpResponse("You're logged out.")

# Create your views here.
def test1(request):
    return HttpResponse("<h2>test 1</h2>")


