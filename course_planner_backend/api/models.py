from django.conf import settings
from django.db import models


class Course(models.Model):
    """A teacher-owned course that contains topics and lessons."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "title"]

    def __str__(self) -> str:
        return f"{self.title}"


class Topic(models.Model):
    """A topic that belongs to a course."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="topics")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        unique_together = [("course", "title")]

    def __str__(self) -> str:
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    """A scheduled lesson for a given topic (or directly under a course)."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    topic = models.ForeignKey(
        Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name="lessons"
    )
    title = models.CharField(max_length=200)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["start_at", "id"]

    def __str__(self) -> str:
        return f"{self.title} ({self.start_at})"


class Student(models.Model):
    """A student record (simple, teacher-owned) to track progress."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="students"
    )
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name", "id"]
        unique_together = [("owner", "email")]

    def __str__(self) -> str:
        return self.name


class Progress(models.Model):
    """Progress for a student against a topic, optionally tied to a lesson."""

    STATUS_NOT_STARTED = "not_started"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"

    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, "Not started"),
        (STATUS_IN_PROGRESS, "In progress"),
        (STATUS_COMPLETED, "Completed"),
    ]

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="progress"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="progress"
    )
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name="progress"
    )
    lesson = models.ForeignKey(
        Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name="progress"
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_NOT_STARTED
    )
    percent = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "id"]
        unique_together = [("student", "topic")]

    def __str__(self) -> str:
        return f"{self.student} - {self.topic} ({self.status})"
