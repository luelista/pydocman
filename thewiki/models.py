# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
import hashlib
import sys
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import os
from django.db.models import Q

# USER - Permissions
UPERM_ADMINMODE             = 1         # Useraccounts verwalten auf höchstem Level (sperren/entsperren, Gebühren...)
UPERM_IGNORERESTRICTIONS    = 2         # darf auch auf Privatseiten gucken
UPERM_ROOTMODE              = 4         #  --> Expertenmodus an
UPERM_VIEWSOURCE            = 8         # darf viewSource-Ansicht verwenden
UPERM_STATICEDIT            = 16        # Javascript, CSS editieren; Systembilder/icons verändern
UPERM_ALLOWSU               = 32        # substitute user -- forTest
UPERM_DBADMIN               = 64        # dbAdmin
UPERM_MWUPD3                = 128       # mwupd3
UPERM_BETAINVITE            = 256       # darf einladungscodes verteilen
  

# Create your models here.

class Page(models.Model):
    class Meta:
        managed = False
        db_table = "twiki_pages"
    wiki = models.ForeignKey("Wiki", db_column="wid")
    page_key = models.CharField(max_length=32)
    filespec = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    user = models.CharField(max_length=30)
    p_view = models.CharField(max_length=1)
    p_kom = models.CharField(max_length=1)
    p_edit = models.CharField(max_length=1)
    deleted = models.IntegerField()
    parent = models.ForeignKey("Page", db_column="ref_page_id")
    authors = models.CharField(max_length=100)
    pagetype = models.IntegerField()
    spezialseite = models.CharField(max_length=25)
    override_layout = models.CharField(max_length=25)
    keywords = models.CharField(max_length=100)
    META_description = models.TextField()
    META_keywords = models.TextField()
    link_image = models.TextField()
    comment = models.TextField()
    sort_order = models.IntegerField()
    lastedit = models.DateField()
    lastedit_by = models.CharField(max_length=25)
    lastmodified = models.DateField()
    lastmodified_by = models.CharField(max_length=25)
    lastmodified_thru = models.IntegerField()
    lastmodified_text = models.CharField(max_length=25)
    created = models.DateField()
    created_by = models.CharField(max_length=25)
    lastblogged = models.DateField()
    lastblogged_by = models.CharField(max_length=25)
    
    def __str__(self):
        return self.filespec + " : " + self.title
    
    def get_content(self, type=None):
        suffix = ''
        if type != None:
            suffix = '.' + type
        pagefile = settings.THEWIKI_PAGE_DIR + '/' + str(self.id) + suffix + '.twpage'
        
        with open(pagefile) as f:
            s = f.read()
        
        return s


class MyUserManager(BaseUserManager):
    # ...
    def get_by_natural_key(self, username):
        print >>sys.stderr, "get"+username
        u = self.get(**{self.model.USERNAME_FIELD: username})
        print >>sys.stderr, u.password
        return u
    
    dummy = None


class User(models.Model):
    class Meta:
        managed = False
        db_table = "twiki_users"
    
    REQUIRED_FIELDS = [ 'fullname' ]
    USERNAME_FIELD = 'username'
    
    objects = MyUserManager()
    
    def has_perm(self, perm, obj=None):
        print >>sys.stderr, "Does the user have a specific permission?", perm, obj
        if perm == "thewiki" or perm == "auth" or perm == "dropmefiles":
            if self.permissions & UPERM_ADMINMODE != 0:
                return True
        return True
    
    def has_module_perms(self, app_label):
        if app_label == "thewiki" or app_label == "auth" or app_label == "dropmefiles":
            if self.permissions & UPERM_ADMINMODE != 0:
                return True
        return False
    
    def get_username(self):
        return getattr(self, self.USERNAME_FIELD)
    
    def __str__(self):
        return self.get_username()
    
    def natural_key(self):
        return (self.get_username(),)
    
    def is_anonymous(self):
        return False
    
    def is_authenticated(self):
        return True
    
    def set_password(self, raw_password):
        self.password = self.make_password(raw_password)
    
    def get_full_name(self):
        return self.fullname
    
    def get_short_name(self):
        return self.username
    
    def check_password(self, password):
        return self.make_password(password) == self.password
    
    def make_password(self, password):
        hash = hashlib.md5(settings.PASSWORD_SALT + password).hexdigest()
        print >>sys.stderr, "make_password: " + hash
        return hash
    
    def has_usable_password(self):
        return self.is_password_usable(self.password)
    
    def is_password_usable(password):
        return len(password) == 32
    
    is_active = True
    is_superuser = True
    is_staff = True
    
    id = models.AutoField(primary_key=True, db_column="id")
    username = models.CharField(max_length=30, unique=True)
    domain = models.CharField(max_length=50)
    password = models.CharField(max_length=32)
    isteam = models.IntegerField()
    permissions = models.IntegerField()
    userflags = models.IntegerField()
    flags = models.IntegerField()
    joinmode = models.IntegerField()
    lock_mode = models.IntegerField()
    fullname = models.CharField(max_length=40)
    sitetitle = models.CharField(max_length=60)
    sitetitle_browser = models.CharField(max_length=60)
    rang = models.CharField(max_length=45)
    description = models.TextField()
    design_id = models.CharField(max_length=20)
    profile_image = models.CharField(max_length=100)
    email = models.CharField(max_length=50)
    ein_dat = models.DateField()
    invitation_code = models.CharField(max_length=10)
    gender = models.IntegerField()
    birth_dat = models.DateField()
    facebook_uid = models.IntegerField()
    twitter_uid = models.IntegerField()
    login_secret = models.CharField(max_length=30)
    
    last_login = models.DateField()

def wiki_load_for_host(request, username):
    request.wiki_name = username
    try:
        try:
            domain = Domain.objects.get(domain=username)
            print "domain found", domain.wiki
            request.wiki = domain.wiki
        except:
            print "domain not found", username
            request.wiki = Wiki.objects.get(wid=username)
    except:
        print "wiki id not found", username
        request.wiki = None

class Wiki(models.Model):
    class Meta:
        managed = False
        db_table = "twiki_wikis"
    wid = models.AutoField(primary_key=True)
    user = models.ForeignKey("User", db_column="uid")
    domain = models.CharField(max_length=50)
    flags = models.IntegerField()
    lock_mode = models.IntegerField()
    sitetitle = models.CharField(max_length=60)
    sitetitle_browser = models.CharField(max_length=60)
    description = models.TextField()
    design_id = models.CharField(max_length=20)
    ein_dat = models.DateField()
    lastmodified = models.DateField()
    
    def __str__(self):
        try:
            d = self.all_domains.get(assignment_status=1)
            return d.domain
        except ObjectDoesNotExist:
            return "[orphaned wiki]"
            
    

class Domain(models.Model):
    class Meta:
        managed = False
        db_table = "twiki_domains"
    id = models.AutoField(primary_key=True)
    wiki = models.ForeignKey("Wiki", db_column="wid", related_name="all_domains")
    tld = models.CharField(max_length=20)
    sld = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    owner = models.ForeignKey("User", db_column="owner_uid", related_name="my_domains")
    system = models.IntegerField()
    assignment_status = models.IntegerField()
    ein_dat = models.DateField()
    expiration_dat = models.DateField()
    
class UserlinkManager(models.Manager):
    def contacts(self, user):
        return self.filter(Q(user_a=user) | Q(user_b=user)).filter(is_team=0)
    
    def contact_names(self, user):
        contacts = self.contacts(user)
        return [link.other_name(user.username) for link in contacts]


class Userlink(models.Model):
    class Meta:
        managed = False
        db_table = "twiki_userlink"
    objects = UserlinkManager()
    
    ulid = models.AutoField(primary_key=True, db_column="id")
    user_a = models.CharField(max_length=25)  #models.ForeignKey("User", db_column="user_a", related_name="username")
    user_b = models.CharField(max_length=25)  #models.ForeignKey("User", db_column="user_b", related_name="username")
    is_team = models.IntegerField()
    status = models.IntegerField()
    notify_flag = models.IntegerField(db_column="notifyFlag")
    rang = models.CharField(max_length=45)
    created = models.DateTimeField()
    
    def other_name(self, theName):
        if theName == self.user_a:
            return self.user_b
        else:
            return self.user_a
