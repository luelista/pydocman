from django.contrib import admin
from django.contrib.admin.decorators import register

from dropme.models import Document, Clipboard

@register(Clipboard)
class ClipboardAdmin(admin.ModelAdmin):
    pass

@register(Document)
class DocumentAdmin(admin.ModelAdmin):
    pass
