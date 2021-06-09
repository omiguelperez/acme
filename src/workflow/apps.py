from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WorkflowAppConfig(AppConfig):

    name = 'src.workflow'
    verbose_name = _('Workflow')
