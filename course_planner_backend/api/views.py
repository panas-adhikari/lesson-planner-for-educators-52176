from django.contrib.auth import login, logout
from django.db.models import Count
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Course, Lesson, Progress, Student, Topic
from .serializers import (
    CourseSerializer,
    LessonSerializer,
    LoginSerializer,
    ProgressSerializer,
    RegisterSerializer,
    StudentSerializer,
    TopicSerializer,
    UserSerializer,
)


@api_view(["GET"])
@permission_classes([AllowAny])
# PUBLIC_INTERFACE
def health(request):
    """Health check endpoint.

    Returns:
        JSON message confirming the server is running.
    """
    return Response({"message": "Server is up!"})


@api_view(["POST"])
@permission_classes([AllowAny])
# PUBLIC_INTERFACE
def register(request):
    """Register a new user (session-based auth).

    Body:
        email: string
        password: string
        name: string (optional)

    Returns:
        201 with user payload.
    """
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    login(request, user)
    return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
# PUBLIC_INTERFACE
def login_view(request):
    """Log in a user and create a session cookie.

    Body:
        email: string
        password: string

    Returns:
        200 with user payload.
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data["user"]
    login(request, user)
    return Response(UserSerializer(user).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
# PUBLIC_INTERFACE
def logout_view(request):
    """Log out current user and clear session.

    Returns:
        200 with message.
    """
    logout(request)
    return Response({"message": "Logged out"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
# PUBLIC_INTERFACE
def me(request):
    """Get current authenticated user.

    Returns:
        200 with user payload.
    """
    return Response(UserSerializer(request.user).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
# PUBLIC_INTERFACE
def dashboard(request):
    """Get simple dashboard stats for the logged-in teacher.

    Returns:
        { courses_count, topics_count, lessons_count, students_count, progress_completed_count }
    """
    courses_qs = Course.objects.filter(owner=request.user)
    topics_qs = Topic.objects.filter(course__owner=request.user)
    lessons_qs = Lesson.objects.filter(course__owner=request.user)
    students_qs = Student.objects.filter(owner=request.user)
    completed_progress = Progress.objects.filter(
        course__owner=request.user, status=Progress.STATUS_COMPLETED
    )

    return Response(
        {
            "courses_count": courses_qs.count(),
            "topics_count": topics_qs.count(),
            "lessons_count": lessons_qs.count(),
            "students_count": students_qs.count(),
            "progress_completed_count": completed_progress.count(),
        }
    )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
# PUBLIC_INTERFACE
def courses(request):
    """List or create courses for the current teacher.

    GET returns list of courses.
    POST creates course: {title, description}
    """
    if request.method == "GET":
        qs = Course.objects.filter(owner=request.user)
        return Response(CourseSerializer(qs, many=True).data)

    serializer = CourseSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    course = Course.objects.create(owner=request.user, **serializer.validated_data)
    return Response(CourseSerializer(course).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
# PUBLIC_INTERFACE
def course_detail(request, course_id: int):
    """Retrieve/update/delete a single course (teacher-owned)."""
    try:
        course = Course.objects.get(id=course_id, owner=request.user)
    except Course.DoesNotExist:
        return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(CourseSerializer(course).data)

    if request.method == "PUT":
        serializer = CourseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        for field, value in serializer.validated_data.items():
            setattr(course, field, value)
        course.save()
        return Response(CourseSerializer(course).data)

    course.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
# PUBLIC_INTERFACE
def topics(request, course_id: int):
    """List or create topics under a course."""
    try:
        course = Course.objects.get(id=course_id, owner=request.user)
    except Course.DoesNotExist:
        return Response({"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        qs = Topic.objects.filter(course=course)
        return Response(TopicSerializer(qs, many=True).data)

    serializer = TopicSerializer(data={**request.data, "course": course.id})
    serializer.is_valid(raise_exception=True)
    topic = Topic.objects.create(**serializer.validated_data)
    return Response(TopicSerializer(topic).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
# PUBLIC_INTERFACE
def topic_detail(request, topic_id: int):
    """Retrieve/update/delete a topic (teacher-owned via its course)."""
    try:
        topic = Topic.objects.select_related("course").get(
            id=topic_id, course__owner=request.user
        )
    except Topic.DoesNotExist:
        return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(TopicSerializer(topic).data)

    if request.method == "PUT":
        serializer = TopicSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Course cannot change via this endpoint; keep current
        for field, value in serializer.validated_data.items():
            if field == "course":
                continue
            setattr(topic, field, value)
        topic.save()
        return Response(TopicSerializer(topic).data)

    topic.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
# PUBLIC_INTERFACE
def lessons(request, course_id: int):
    """List or create lessons under a course."""
    try:
        course = Course.objects.get(id=course_id, owner=request.user)
    except Course.DoesNotExist:
        return Response({"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        qs = Lesson.objects.filter(course=course).select_related("topic")
        return Response(LessonSerializer(qs, many=True).data)

    serializer = LessonSerializer(data={**request.data, "course": course.id})
    serializer.is_valid(raise_exception=True)

    # Validate topic belongs to course if provided
    topic_id = serializer.validated_data.get("topic")
    if topic_id:
        if not Topic.objects.filter(id=topic_id.id, course=course).exists():
            return Response(
                {"detail": "Topic does not belong to course"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    lesson = Lesson.objects.create(**serializer.validated_data)
    return Response(LessonSerializer(lesson).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
# PUBLIC_INTERFACE
def lesson_detail(request, lesson_id: int):
    """Retrieve/update/delete a lesson (teacher-owned via its course)."""
    try:
        lesson = Lesson.objects.select_related("course").get(
            id=lesson_id, course__owner=request.user
        )
    except Lesson.DoesNotExist:
        return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(LessonSerializer(lesson).data)

    if request.method == "PUT":
        serializer = LessonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Course cannot change via this endpoint; keep current
        for field, value in serializer.validated_data.items():
            if field == "course":
                continue
            setattr(lesson, field, value)
        lesson.save()
        return Response(LessonSerializer(lesson).data)

    lesson.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
# PUBLIC_INTERFACE
def students(request):
    """List or create students for the current teacher."""
    if request.method == "GET":
        qs = Student.objects.filter(owner=request.user)
        return Response(StudentSerializer(qs, many=True).data)

    serializer = StudentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    student = Student.objects.create(owner=request.user, **serializer.validated_data)
    return Response(StudentSerializer(student).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
# PUBLIC_INTERFACE
def student_detail(request, student_id: int):
    """Retrieve/update/delete a student record (teacher-owned)."""
    try:
        student = Student.objects.get(id=student_id, owner=request.user)
    except Student.DoesNotExist:
        return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(StudentSerializer(student).data)

    if request.method == "PUT":
        serializer = StudentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        for field, value in serializer.validated_data.items():
            setattr(student, field, value)
        student.save()
        return Response(StudentSerializer(student).data)

    student.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
# PUBLIC_INTERFACE
def progress_list_create(request, course_id: int):
    """List or create progress entries for a given course.

    GET: list progress rows for course (teacher-owned).
    POST: create/overwrite progress for a student+topic.
    """
    try:
        course = Course.objects.get(id=course_id, owner=request.user)
    except Course.DoesNotExist:
        return Response({"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        qs = Progress.objects.filter(course=course).select_related("student", "topic")
        return Response(ProgressSerializer(qs, many=True).data)

    serializer = ProgressSerializer(data={**request.data, "course": course.id})
    serializer.is_valid(raise_exception=True)

    student = serializer.validated_data["student"]
    topic = serializer.validated_data["topic"]

    # Ensure ownership + topic in course
    if student.owner_id != request.user.id:
        return Response(
            {"detail": "Student not found"}, status=status.HTTP_404_NOT_FOUND
        )
    if topic.course_id != course.id:
        return Response(
            {"detail": "Topic does not belong to course"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    progress, _created = Progress.objects.update_or_create(
        student=student,
        topic=topic,
        defaults=serializer.validated_data,
    )
    return Response(ProgressSerializer(progress).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
# PUBLIC_INTERFACE
def course_stats(request, course_id: int):
    """Return course stats used by frontend (topics count, lessons count, progress counts)."""
    try:
        course = Course.objects.get(id=course_id, owner=request.user)
    except Course.DoesNotExist:
        return Response({"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

    topic_count = Topic.objects.filter(course=course).count()
    lesson_count = Lesson.objects.filter(course=course).count()
    progress_by_status = (
        Progress.objects.filter(course=course)
        .values("status")
        .annotate(count=Count("id"))
    )
    status_map = {row["status"]: row["count"] for row in progress_by_status}

    return Response(
        {
            "course_id": course.id,
            "topic_count": topic_count,
            "lesson_count": lesson_count,
            "progress": {
                "not_started": status_map.get(Progress.STATUS_NOT_STARTED, 0),
                "in_progress": status_map.get(Progress.STATUS_IN_PROGRESS, 0),
                "completed": status_map.get(Progress.STATUS_COMPLETED, 0),
            },
        }
    )
