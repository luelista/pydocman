from django.shortcuts import render
from django.http import HttpResponse, Http404
from thewiki.models import Page

# Create your views here.

def index(request):
  out = "<h4>thewiki response:</h4>"
  if hasattr( request, 'wiki_name'):
    out += " <p>wiki_name: %s </p>" % (request.wiki_name)
  else:
    out += "no wiki"
  if request.wiki != None:
    out += "<p> wiki domain: %s, id: %d, title: %s</p>" % (
          request.wiki.domain, request.wiki.wid, request.wiki.sitetitle)
  
  return HttpResponse(out)


def disp_page(request):
  if request.wiki == None:
    raise Http404("Wiki not found")
  
  try:
    page = Page.objects.get(wiki=request.wiki, filespec=request.path_info)
    if page.p_view != "*":
      return HttpResponse("Forbidden (%s)" % (page.p_view))
    
    return render(request, "thewiki/pagedisplay.html", { "info": request.path_info, "page": page })
    
  except Page.DoesNotExist:
    raise Http404("Page not found")


def pagelist(request):
  if request.wiki == None:
    raise Http404("Wiki not found")
  
  pages = Page.objects.filter(wiki=request.wiki).order_by("-lastmodified")
  
  return render(request, "thewiki/pagelist.html", { "wiki": request.wiki, "pages": pages })
  

def default_page(request):
  print request.META
  return render(request, "thewiki/default_page.html", {})


