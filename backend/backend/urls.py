from django.contrib import admin
from django.urls import path

from django.urls import path, include
from appointment.views import AppointmentViewSet
from rest_framework.routers import DefaultRouter
from human_resource.views import EmployeeViewSet, DepartmentViewSet

router = DefaultRouter()
router.register(r"employees", EmployeeViewSet)
router.register(r"departments", DepartmentViewSet)
router.register(r"appointments", AppointmentViewSet)


urlpatterns = [
    path("api/", include(router.urls)),
    path("admin/", admin.site.urls),
]
