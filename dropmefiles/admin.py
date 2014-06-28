from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.html import format_html


# Register your models here.
from dropmefiles.models import Clipboard, Item


class WikiAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'sitetitle']


class ItemsInline(admin.TabularInline):
    model = Item
    fields = [ 'filename', 'comment', 'admin_link', 'lastmodified' ]
    readonly_fields = [ 'filename', 'comment', 'admin_link', 'lastmodified' ]
    ordering = ['-lastmodified']
    can_delete = False
    can_add = False
    max_num = 0
    extra = 0
    
    def admin_link(self, instance):
        url = reverse('admin:%s_%s_change' % (instance._meta.app_label,  
                                              instance._meta.module_name),
                      args=(instance.cid,))
        return format_html(u'<a href="{}">Edit Item Details</a>', url)
        # ? or if you want to include other fields:
        #return format_html(u'<a href="{}">Edit: {}</a>', url, instance.title)



class ClipboardAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'owner', 'state', 'lastmodified']
    list_filter = ['state', 'owner']
    ordering = ['-lastmodified']
    inlines = [ ItemsInline ]
    def ownerusername(self, item):
        return item.owner.username
    
    """
    removes the doubled item captions from ItemsInline
    """
    def render_change_form(self, request, context, *args, **kwargs):
        def get_queryset(original_func):
            import inspect, itertools
            def wrapped_func():
                if inspect.stack()[1][3] == '__iter__':
                    return itertools.repeat(None)
                return original_func()
            return wrapped_func
            
        for formset in context['inline_admin_formsets']:
            formset.formset.get_queryset = get_queryset(formset.formset.get_queryset)
            
        return super(ClipboardAdmin, self).render_change_form(request, context,*args, **kwargs)
    

admin.site.register(Clipboard, ClipboardAdmin)
admin.site.register(Item)

