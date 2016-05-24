from django.apps import AppConfig

class DropmeConfig(AppConfig):
    name = 'dropme'
    def ready(self):
        from actstream import registry
        from django.apps import apps as django_apps

        registry.register(self.get_model('Clipboard'))
        registry.register(self.get_model('Document'))
        registry.register(django_apps.get_model('auth.User'))


