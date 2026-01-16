from django.apps import AppConfig
from django.db.models.signals import post_migrate


class OrganizationsConfig(AppConfig):
    name = "organizations"

    def ready(self):
        from .signals import create_default_plan
        post_migrate.connect(create_default_plan, sender=self)
