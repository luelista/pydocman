from django import template
from django.core.urlresolvers import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def url_active(context, *args, **kwargs):
    if 'request' not in context:
        return ''
    request = context['request']
    
    url = reverse(args[0], args=args[1:], kwargs=kwargs)
    #if request.resolver_match.url_name in args:
    if url == request.path:
        return ' class="active" href="%s" ' % (url)
    else:
        return ' href="%s" ' % (url)

