from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("add/", views.add_device, name="add_device"),
    path("device/<int:device_id>/update/", views.update_device, name="update_device"),
    path("api/devices/", views.api_devices, name="api_devices"),
]
