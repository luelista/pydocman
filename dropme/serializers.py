from django.contrib.auth.models import User
from dropme.models import Clipboard, Document
from rest_framework import serializers


class ClipboardSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Clipboard
        #fields = ()

class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Document
        #fields = ()

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User


