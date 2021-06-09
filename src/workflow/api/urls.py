from django.urls import path
from src.workflow.api import views

app_name = 'workflow'

urlpatterns = [
    path(
        'upload/',
        views.WorkflowFileUploadView.as_view(),
        name=views.WorkflowFileUploadView.name
    ),
]
