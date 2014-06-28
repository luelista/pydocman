from django.contrib import admin

# Register your models here.
from thewiki.models import User, Page, Wiki


class WikiAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'sitetitle']

class PageAdmin(admin.ModelAdmin):
    list_display = ['id', 'filespec', 'title', 'lastmodified']
    list_filter = ['wiki']
    def has_add_permission(self, something):
        return True


admin.site.register(User)
admin.site.register(Wiki, WikiAdmin)
admin.site.register(Page, PageAdmin)

