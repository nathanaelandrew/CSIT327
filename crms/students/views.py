import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from classes.models import ClassRecord, Enrollment

from .forms import StudentForm
from .models import Student


def student_list(request):
    students = Student.objects.all()

    return render(
        request,
        "students/list.html",
        {
            "students": students,
        },
    )


def student_detail(request, student_id):
    student = get_object_or_404(
        Student,
        id=student_id,
    )

    enrollments = (
        Enrollment.objects
        .filter(student=student)
        .select_related("class_record")
    )

    return render(
        request,
        "students/detail.html",
        {
            "student": student,
            "enrollments": enrollments,
        },
    )


def student_create(request):
    if request.method == "POST":
        form = StudentForm(request.POST)

        if form.is_valid():
            student = form.save()
            messages.success(
                request,
                f"Student {student.first_name} {student.last_name} was created.",
            )
            return redirect("students:detail", student_id=student.id)
    else:
        form = StudentForm()

    return render(
        request,
        "students/form.html",
        {
            "form": form,
        },
    )


def students_by_class(request, class_id):
    class_record = get_object_or_404(
        ClassRecord,
        id=class_id,
    )

    enrollments = (
        Enrollment.objects
        .filter(class_record=class_record)
        .select_related("student")
    )

    return render(
        request,
        "students/by_class.html",
        {
            "class_record": class_record,
            "enrollments": enrollments,
        },
    )


@require_GET
def students_by_class_json(request, class_id):
    class_record = get_object_or_404(
        ClassRecord,
        id=class_id,
    )

    enrollments = (
        Enrollment.objects
        .filter(class_record=class_record)
        .select_related("student")
    )

    students = [
        {
            "id": enrollment.student.id,
            "student_id": enrollment.student.student_id,
            "name": (
                f"{enrollment.student.first_name} "
                f"{enrollment.student.last_name}"
            ),
            "email": enrollment.student.email,
        }
        for enrollment in enrollments
    ]

    return JsonResponse(
        {
            "class_id": class_record.id,
            "subject_code": class_record.subject_code,
            "subject_name": class_record.subject_name,
            "students": students,
        }
    )


@require_POST
def enroll_student(request, class_id):
    class_record = get_object_or_404(
        ClassRecord,
        id=class_id,
    )

    try:
        data = json.loads(request.body)
        student_id = data.get("student_id")
    except (json.JSONDecodeError, TypeError):
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid JSON request.",
            },
            status=400,
        )

    if not student_id:
        return JsonResponse(
            {
                "success": False,
                "message": "student_id is required.",
            },
            status=400,
        )

    student = get_object_or_404(
        Student,
        id=student_id,
    )

    enrollment, created = Enrollment.objects.get_or_create(
        student=student,
        class_record=class_record,
    )

    return JsonResponse(
        {
            "success": True,
            "created": created,
            "message": (
                f"{student.first_name} {student.last_name} "
                f"{'was enrolled.' if created else 'is already enrolled.'}"
            ),
            "enrollment_id": enrollment.id,
        }
    )
