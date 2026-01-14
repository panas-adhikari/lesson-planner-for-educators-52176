from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from .models import Course, Lesson, Progress, Student, Topic

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serialize basic user fields for frontend display."""

    class Meta:
        model = User
        fields = ["id", "username", "email"]


class RegisterSerializer(serializers.Serializer):
    """Register a new user with email/password."""

    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    name = serializers.CharField(required=False, allow_blank=True, default="")

    # PUBLIC_INTERFACE
    def create(self, validated_data):
        """Create a new Django user."""
        email = validated_data["email"].strip().lower()
        password = validated_data["password"]
        name = validated_data.get("name", "").strip()

        # Use email as username for simplicity.
        user = User.objects.create_user(username=email, email=email, password=password)
        if name:
            # Works for default User model: first_name/last_name exist
            user.first_name = name
            user.save(update_fields=["first_name"])
        return user


class LoginSerializer(serializers.Serializer):
    """Login with email/password (session-based)."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    # PUBLIC_INTERFACE
    def validate(self, attrs):
        """Validate credentials and return the authenticated user."""
        email = attrs["email"].strip().lower()
        password = attrs["password"]

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        attrs["user"] = user
        return attrs


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "title", "description", "created_at"]


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ["id", "course", "title", "description", "order"]


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "course", "topic", "title", "start_at", "end_at", "notes"]


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["id", "name", "email", "created_at"]


class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = [
            "id",
            "student",
            "course",
            "topic",
            "lesson",
            "status",
            "percent",
            "notes",
            "updated_at",
        ]
