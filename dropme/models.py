import re

from django.conf import settings
from django.contrib.admin.decorators import register
from django.core.urlresolvers import reverse
from django.db import models
import uuid
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
        if user is None: return None
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



def random_token_doc():
    return random_token(12)


class Document(models.Model):
    class Meta:
        pass
        # db_table = "twiki_clipitem"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clipboard = models.ForeignKey("Clipboard", db_column="cbid")  # doc_mandant

    title = models.CharField(max_length=80)  # title
    url_filename = models.CharField(max_length=80)

    # ??? private_flags = models.IntegerField()
    # wird vmtl nicht benötigt??? sort_index = models.IntegerField()

    doc_date = models.DateField(auto_now_add=True)

    filetype = models.CharField(max_length=20)
    subtype = models.CharField(max_length=20)
    filesize = models.IntegerField()   # file_size
    page_count = models.IntegerField()  #page_count
        # relevant for PDF documents (and similar stuff)

    tags = models.ManyToManyField("Tag", through='DocumentTag')  # tags
    comment = models.TextField() # description

    # ??? properties = models.IntegerField()
    source_url = models.TextField()
    source_title = models.TextField()       # import_source
    uploader_ip = models.CharField(max_length=50)
    # ??? upload_via = models.IntegerField()

    created_by = models.ForeignKey("auth.User", related_name="documents_created_by")
    updated_by = models.ForeignKey("auth.User", related_name="documents_updated_by")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    readonly_token = models.CharField(max_length=12, default=random_token_doc, unique=True)

    def full_dir(self):
        return settings.DROPME_STORE_DIRECTORY + self.created_at.strftime("%Y-%m-%d") + "_" + str(self.cid) + "/"

    def read_file_contents(self):
        with open(self.full_path(), "r") as myfile:
            return myfile.read()

    def get_url_args(self):
        return self.clipboard.get_url_args() + { 'url_filename': self.url_filename, 'doc_id': self.id }

    def __str__(self):
        return self.title

class DocumentTag(models.Model):
    tag = models.ForeignKey("Tag")
    document = models.ForeignKey("Document")
    value = models.CharField(max_length=50)

class Tag(models.Model):
    keyword = models.CharField(max_length=50)


