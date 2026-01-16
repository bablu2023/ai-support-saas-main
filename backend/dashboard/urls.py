from django.urls import path
from .views import widget_page, upload_page, logs_page
from .views import dashboard_home
from .views import pricing_page

urlpatterns = [
    path("widget/", widget_page),
    path("upload/", upload_page),
    path("logs/", logs_page),
    path("", dashboard_home, name="dashboard"),
    path("pricing/", pricing_page, name="pricing"),
]



