from django.urls import path
from . import views

urlpatterns = [
    path("", views.student_list),  # Adjust 'views.student_list' if your view function has a different name
]