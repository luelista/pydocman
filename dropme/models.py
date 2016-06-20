from datetime import datetime

from subprocess import check_output, check_call

import os
from dropme.docinfos import ImageDocInfo, DocInfo, PdfDocInfo
from os import stat

import re
from actstream import action
from django.conf import settings
from django.contrib.admin.decorators import register
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse
from django.db import models
import uuid

from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.utils.text import slugify

from dropme.helper import random_token


class UserPermission(models.Model):
    clipboard = models.ForeignKey("Clipboard")
    for_user = models.ForeignKey("auth.User")
    allow_view = models.BooleanField(default=True)
    allow_add_documents = models.BooleanField(default=False)
    allow_change = models.BooleanField(default=False)
    allow_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)


class GroupPermission(models.Model):
    clipboard = models.ForeignKey("Clipboard")
    for_group = models.ForeignKey("auth.Group")
    allow_view = models.BooleanField(default=True)
    allow_add_documents = models.BooleanField(default=False)
    allow_change = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)


def random_token_clipboard():
    return random_token(9)

class Clipboard(models.Model):
    class Meta:
        pass
        # managed = False
        # db_table = "clipboard"

    id = models.AutoField(primary_key=True)
    token = models.CharField(max_length=9, default=random_token_clipboard, unique=True)
    title = models.CharField(blank=True, max_length=50)
    viewmode = models.CharField(max_length=10, default="tile")
    sortorder = models.CharField(max_length=10, default="upload")
    listable = models.BooleanField(default=False)
    indexed = models.BooleanField(default=False)
    created_by = models.ForeignKey("auth.User", related_name="clipboards_created_by")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    icon = models.CharField(max_length=90)

    users = models.ManyToManyField("auth.User", through='UserPermission')
    groups = models.ManyToManyField("auth.Group", through='GroupPermission')
    allow_public_view = models.BooleanField(default=True, help_text="Allow anyone with the link to view this clipboard")
    allow_public_add_documents = models.BooleanField(default=False, help_text="Allow anyone with the link to add documents to this clipboards")


    def get_permission_for(self, user):
        if user is None or isinstance(user, AnonymousUser): return None
        try:
            userPerm = UserPermission.objects.get(clipboard=self, for_user=user)
            return userPerm
        except UserPermission.DoesNotExist:
            try:
                groupPerm = GroupPermission.objects.get(clipboard=self, for_group__user_set=user)
                return groupPerm
            except GroupPermission.DoesNotExist:
                return None

    def has_view_permission(self, user):
        if self.allow_public_view:
            return True
        perm = self.get_permission_for(user)
        if perm is not None and perm.allow_view:
            return True
        else:
            return False

    def has_add_documents_permission(self, user):
        if self.allow_public_add_documents:
            return True
        perm = self.get_permission_for(user)
        if perm is not None and perm.allow_add_documents:
            return True
        else:
            return False

    def has_change_permission(self, user):
        if self.allow_public_add_documents:
            return True
        perm = self.get_permission_for(user)
        if perm is not None and perm.allow_add_documents:
            return True
        else:
            return False

    def __str__(self):
        return self.title

    def get_slug(self):
        return slugify(self.title)

    def get_url_args(self):
        return { 'slug': self.get_slug(), 'token': self.token } #, 'cbid': self.id

    def get_show_clipboard_url(self):
        return reverse('show_clipboard', kwargs=self.get_url_args())
    def get_absolute_url(self):
        return self.get_show_clipboard_url()


def random_token_doc():
    return random_token(12)

class Document(models.Model):
    class Meta:
        pass
        # db_table = "twiki_clipitem"

    id = models.AutoField(primary_key=True)
    clipboard = models.ForeignKey("Clipboard", db_column="cbid")  # doc_mandant

    title = models.CharField(max_length=80)  # title
    url_filename = models.CharField(max_length=80)

    # ??? private_flags = models.IntegerField()
    # wird vmtl nicht benötigt??? sort_index = models.IntegerField()

    doc_date = models.DateField(default=datetime.today, blank=True, null=True)

    filetype = models.CharField(max_length=20)
    subtype = models.CharField(max_length=20)
    filesize = models.IntegerField()   # file_size
    page_count = models.IntegerField()  #page_count
        # relevant for PDF documents (and similar stuff)
    storage_path = models.CharField(max_length=100)
    storage_filename = models.CharField(max_length=100)

    tags = models.ManyToManyField("Tag", through='DocumentTag')  # tags
    comment = models.TextField() # description

    # ??? properties = models.IntegerField()
    source_url = models.TextField()
    source_name = models.TextField()       # import_source
    uploader_ip = models.CharField(max_length=50)
    # ??? upload_via = models.IntegerField()

    created_by = models.ForeignKey("auth.User", related_name="documents_created_by")
    updated_by = models.ForeignKey("auth.User", related_name="documents_updated_by")

    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    readonly_token = models.CharField(max_length=12, default=random_token_doc, unique=True)

    def set_tags(self, tag_str):
        self.documenttag_set.all().delete()
        for match in re.finditer(r"([^\s=]+)(?::([^\s]+))?", tag_str):
            tag_obj, created = Tag.objects.get_or_create(keyword=match.group(1))
            self.documenttag_set.create(tag=tag_obj, value=match.group(2))

    def get_path(self):
        if not self.storage_path:
            raise RuntimeError("storage_path was not set - model must be saved before using full_dir")
        return settings.DROPME_STORE_DIRECTORY + "/" + self.storage_path + "/"

    def default_dir_name(self):
        return self.created_at.strftime("%Y-%m-%d") + "_" + str(self.cid)

    def get_main_filespec(self):
        return self.get_path() + self.storage_filename

    def get_page_preview_filespec(self, page_number):
        return self.get_path() + '_page' + str(page_number) + '.jpg'

    def get_thumb_filespec(self, page_number = 1):
        return self.get_path() + '_thumb' + str(page_number) + '.jpg'

    def handle_uploaded_file(self, f):
        with open(self.get_main_filespec(), 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

        # generate preview images
        self.docinfo().prepare_preview()

    def read_file_contents(self):
        with open(self.get_main_filespec(), "r") as myfile:
            return myfile.read()

    def get_url_args(self):
        #z = self.clipboard.get_url_args()
        #z['url_filename'] = self.url_filename
        #z['doc_id'] = self.id
        return { 'doc_id': self.id }

    def get_show_document_url(self):
        return reverse('show_document', kwargs=self.get_url_args())

    def docinfo(self):
        if self.filetype == 'image':
            return ImageDocInfo(self)
        elif self.filetype == 'pdf':
            return PdfDocInfo(self)
        else:
            return DocInfo(self)

    def __str__(self):
        return self.title

class DocumentTag(models.Model):
    tag = models.ForeignKey("Tag")
    document = models.ForeignKey("Document")
    value = models.CharField(max_length=50, blank=True, null=True)

class Tag(models.Model):
    keyword = models.CharField(max_length=50)

