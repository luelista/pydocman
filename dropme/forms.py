from django import forms
from django.contrib.auth.models import Group


class CreateClipboardForm(forms.Form):
    title = forms.CharField(label='Title', min_length=2, max_length=50)
    permission_preset = forms.ChoiceField(label='Permissions', choices=(
        ('protected', 'Protected (visible to everyone, editable only by invited users and groups)'),
        ('private', 'Private (only visible to invited users and groups)'),
        ('inbox', 'Inbox (document upload by everyone, viewing and editing only by invited users and groups)'),
    ))
    owner_group = forms.ModelChoiceField(label='Owner', queryset=Group.objects.none(), required=False)

    def __init__(self, session_user, *args, **kwargs):
        super(CreateClipboardForm, self).__init__(*args, **kwargs)
        self.fields['owner_group'].queryset = Group.objects.filter(user=session_user).order_by('name')





