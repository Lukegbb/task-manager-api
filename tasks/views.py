from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Project, Task
from .serializers import ProjectSerializer, RegisterSerializer, TaskSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Create a new user account (public endpoint)."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


class ProjectViewSet(viewsets.ModelViewSet):
    """CRUD for the authenticated user's projects."""

    serializer_class = ProjectSerializer
    search_fields = ("name", "description")
    ordering_fields = ("name", "created_at")

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user).prefetch_related("tasks")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["get"])
    def stats(self, request, pk=None):
        """Number of tasks per status for a project."""
        project = self.get_object()
        data = project.tasks.aggregate(
            total=Count("id"),
            todo=Count("id", filter=Q(status=Task.Status.TODO)),
            in_progress=Count("id", filter=Q(status=Task.Status.IN_PROGRESS)),
            done=Count("id", filter=Q(status=Task.Status.DONE)),
        )
        return Response(data)


class TaskViewSet(viewsets.ModelViewSet):
    """CRUD for tasks that belong to the authenticated user's projects."""

    serializer_class = TaskSerializer
    filterset_fields = ("project", "status", "priority", "due_date")
    search_fields = ("title", "description")
    ordering_fields = ("priority", "due_date", "created_at")

    def get_queryset(self):
        return Task.objects.filter(project__owner=self.request.user).select_related("project")
