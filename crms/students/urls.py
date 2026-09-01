from django.urls import path

from . import views

app_name = "students"

urlpatterns = [
    path(
        "",
        views.student_list,
        name="list",
    ),
    path(
        "create/",
        views.student_create,
        name="create",
    ),
    path(
        "class/<int:class_id>/",
        views.students_by_class,
        name="by_class",
    ),
    path(
        "<int:student_id>/",
        views.student_detail,
        name="detail",
    ),
]
