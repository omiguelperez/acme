from rest_framework.generics import CreateAPIView

from src.workflow.api.serializers import WorkflowFileUploadSerializer
from src.workflow.models import Upload


class WorkflowFileUploadView(CreateAPIView):

    name = 'upload'
    queryset = Upload.objects.all()
    serializer_class = WorkflowFileUploadSerializer
