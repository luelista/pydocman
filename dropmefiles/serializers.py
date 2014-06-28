from thewiki.models import User
from dropmefiles.models import Clipboard, Item
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'clipboard_set')


class ClipboardSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Clipboard
        fields = ('owner', 'name', 'description', 'item_set')


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Item
        fields = ('filename', 'comment', 'filetype', 'subtype', 'server_filespec', 'url_filename')


