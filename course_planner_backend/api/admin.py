from django.contrib import admin

from .models import Course, Lesson, Progress, Student, Topic


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "created_at")
    search_fields = ("title", "description", "owner__username", "owner__email")
    list_filter = ("created_at",)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "course", "order")
    search_fields = ("title", "description", "course__title")
    list_filter = ("course",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "course", "topic", "start_at", "end_at")
    search_fields = ("title", "notes", "course__title", "topic__title")
    list_filter = ("course", "start_at")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "owner", "created_at")
    search_fields = ("name", "email", "owner__username", "owner__email")
    list_filter = ("created_at",)


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "course", "topic", "status", "percent", "updated_at")
    search_fields = ("student__name", "course__title", "topic__title", "notes")
    list_filter = ("status", "course", "updated_at")
