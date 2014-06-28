from thewiki.models import User
from dropmefiles.models import Clipboard, Item
from rest_framework import viewsets
from dropmefiles.serializers import UserSerializer, ClipboardSerializer, ItemSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ClipboardViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Clipboard.objects.all()
    serializer_class = ClipboardSerializer


class ItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

