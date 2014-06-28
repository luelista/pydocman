from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse

from thewiki.models import User
from django.utils.encoding import python_2_unicode_compatible
import json

# Create your models here.

@python_2_unicode_compatible
class Clipboard(models.Model):
    STATE_PRIVATE = 1
    STATE_PROTECTED = 2
    STATE_PUBLIC = 3
    STATE_CHOICES = (
        (STATE_PRIVATE, 'Private'),
        (STATE_PROTECTED, 'Protected'),
        (STATE_PUBLIC, 'Public')
    )
    class Meta:
        managed = False
        db_table = "twiki_clipboard"
    cbid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=60)
    owner = models.ForeignKey("thewiki.User", db_column="owner", to_field="username")
    description = models.TextField()
    state = models.IntegerField(choices=STATE_CHOICES)
    viewmode = models.CharField(max_length=10)
    sortorder = models.CharField(max_length=10)
    temp = models.IntegerField()
    listable = models.IntegerField()
    indexed = models.IntegerField()
    invited_edit_all = models.IntegerField()
    invited_no_temp = models.IntegerField()
    comments = models.IntegerField()
    deleted = models.IntegerField()
    created = models.DateTimeField()
    lastmodified = models.DateTimeField()
    icon = models.CharField(max_length=90)
    
    def view_perm_of(self, user):
        if self.state == Clipboard.STATE_PRIVATE and user != self.owner:
            #if invited:
            #   return True
            return False
        else:
            return True
    
    def upload_perm_of(self, user):
        if self.state == Clipboard.STATE_PUBLIC:
            return True
        if self.owner == user:
            return True
        #if invited with write permission:
        #   return true
        return False
    
    
    def __str__(self):
        return self.name + " : " + self.description



@python_2_unicode_compatible
class Item(models.Model):
    class Meta:
        managed = False
        db_table = "twiki_clipitem"
    cid = models.AutoField(primary_key=True)
    clipboard = models.ForeignKey("Clipboard", db_column="cbid")
    
    title = models.CharField(max_length=80)
    filename = models.CharField(max_length=80)
    url_filename = models.CharField(max_length=80)
    server_filespec = models.CharField(max_length=180)
    
    private_flags = models.IntegerField()
    sort_index = models.IntegerField()
    
    created_by = models.CharField(max_length=25)
    created = models.DateTimeField()
    lastmodified_by = models.CharField(max_length=25)
    lastmodified = models.DateTimeField()
    
    filetype = models.CharField(max_length=20)
    subtype = models.CharField(max_length=20)
    filesize = models.IntegerField()
    
    deleted = models.IntegerField()
    properties = models.IntegerField()
    source_url = models.TextField()
    source_title = models.TextField()
    
    tags = models.CharField(max_length=100)
    categories = models.CharField(max_length=100)
    comment = models.TextField()
    
    uploader_ip = models.CharField(max_length=20)
    upload_via = models.IntegerField()
    
    def raw_url(self):
        return reverse("show_raw_item",args=( self.clipboard.owner_id, self.clipboard.name, self.url_filename))
        #return "http://u.dropme.de%s" % self.server_filespec
    
    def preview_url(self):
        return self.raw_url()
    
    def full_path(self):
       return settings.DROPME_STORE_DIRECTORY + self.server_filespec
    
    def read_file_contents(self):
        with open (self.full_path(), "r") as myfile:
            return myfile.read()
    
    def view_url(self):
        return reverse('show_item', args=(self.clipboard.owner_id, self.clipboard.name, self.url_filename))
    
    def __str__(self):
        return self.filename



@python_2_unicode_compatible
class Favorites(models.Model):
    class Meta:
        managed = False
        db_table = "twiki_clipfav"
    cfid = models.AutoField(primary_key=True)
    
    user = models.ForeignKey("thewiki.User", db_column="uid")
    clipboard = models.ForeignKey("Clipboard", db_column="cbid")
    alias = models.CharField(max_length=25)
    tag = models.CharField(max_length=25)
    color = models.CharField(max_length=6)
    
    def __str__(self):
        return self.clipboard.name



@python_2_unicode_compatible
class Events(models.Model):
    class Meta:
        managed = False
        db_table = "twiki_clipevent"
    ceid = models.AutoField(primary_key=True)
    
    user = models.ForeignKey("thewiki.User", db_column="actor", to_field="username")
    clipboard = models.ForeignKey("Clipboard", db_column="cbid")
    type = models.CharField(max_length=10)
    subtype = models.CharField(max_length=10)
    data = models.TextField()
    created = models.DateTimeField(db_column="ein_dat")
    
    def get_item(self):
        try:
            itemid = self.get_data()['cid']
            return Item.objects.get(cid=itemid)
        except (AttributeError, Item.DoesNotExist) as ex:
            print "get_item failed", ex
            return None
        
    
    def get_data(self):
        return json.loads(self.data)
    
    
    def __str__(self):
        return self.clipboard.name

    
    
