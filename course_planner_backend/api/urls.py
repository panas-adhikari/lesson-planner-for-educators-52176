from django.urls import path

from .views import (
    course_detail,
    course_stats,
    courses,
    dashboard,
    health,
    lesson_detail,
    lessons,
    login_view,
    logout_view,
    me,
    progress_list_create,
    register,
    student_detail,
    students,
    topic_detail,
    topics,
)

urlpatterns = [
    path("health/", health, name="Health"),
    # Auth
    path("auth/register/", register, name="Register"),
    path("auth/login/", login_view, name="Login"),
    path("auth/logout/", logout_view, name="Logout"),
    path("auth/me/", me, name="Me"),
    # Dashboard
    path("dashboard/", dashboard, name="Dashboard"),
    # Courses
    path("courses/", courses, name="CourseListCreate"),
    path("courses/<int:course_id>/", course_detail, name="CourseDetail"),
    path("courses/<int:course_id>/stats/", course_stats, name="CourseStats"),
    # Topics
    path("courses/<int:course_id>/topics/", topics, name="TopicListCreate"),
    path("topics/<int:topic_id>/", topic_detail, name="TopicDetail"),
    # Lessons
    path("courses/<int:course_id>/lessons/", lessons, name="LessonListCreate"),
    path("lessons/<int:lesson_id>/", lesson_detail, name="LessonDetail"),
    # Students
    path("students/", students, name="StudentListCreate"),
    path("students/<int:student_id>/", student_detail, name="StudentDetail"),
    # Progress
    path(
        "courses/<int:course_id>/progress/",
        progress_list_create,
        name="ProgressListCreate",
    ),
]
