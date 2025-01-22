from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        import core.signals # Keep the signals import here
        super(CoreConfig, self).ready() # Call the parent class's ready method