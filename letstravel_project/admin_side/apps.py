from django.apps import AppConfig


class AdminSideConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_side'

    def ready(self):
        import admin_side.signals
