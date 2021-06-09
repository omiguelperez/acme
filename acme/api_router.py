from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

app_name = 'api'


urlpatterns = [
    # Merkel apps
    path(
        '',
        include(('src.workflow.api.urls', 'src.workflow'),
                namespace='workflow')
    ),
]

urlpatterns += router.urls

