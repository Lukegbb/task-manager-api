from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tasks.models import Project, Task

User = get_user_model()


class AuthTests(APITestCase):
    def test_register_and_obtain_token(self):
        response = self.client.post(
            reverse("register"),
            {"username": "lucas", "email": "lucas@example.com", "password": "Str0ng-pass-123"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", response.data)

        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "lucas", "password": "Str0ng-pass-123"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_endpoints_require_authentication(self):
        response = self.client.get(reverse("project-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProjectTaskTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", password="Str0ng-pass-123")
        self.other = User.objects.create_user("bob", password="Str0ng-pass-123")
        self.client.force_authenticate(self.user)
        self.project = Project.objects.create(owner=self.user, name="Website")

    def test_create_project_sets_owner(self):
        response = self.client.post(reverse("project-list"), {"name": "Mobile app"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["owner"], "alice")

    def test_duplicate_project_name_is_rejected(self):
        response = self.client.post(reverse("project-list"), {"name": "website"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_only_sees_own_projects(self):
        Project.objects.create(owner=self.other, name="Secret")
        response = self.client.get(reverse("project-list"))
        names = [p["name"] for p in response.data["results"]]
        self.assertEqual(names, ["Website"])

    def test_cannot_access_other_users_project(self):
        other_project = Project.objects.create(owner=self.other, name="Secret")
        response = self.client.get(reverse("project-detail", args=[other_project.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_task_and_filter_by_status(self):
        self.client.post(
            reverse("task-list"),
            {"project": self.project.id, "title": "Write tests", "status": "done"},
        )
        self.client.post(reverse("task-list"), {"project": self.project.id, "title": "Deploy"})

        response = self.client.get(reverse("task-list"), {"status": "done"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Write tests")

    def test_cannot_add_task_to_other_users_project(self):
        other_project = Project.objects.create(owner=self.other, name="Secret")
        response = self.client.post(
            reverse("task-list"), {"project": other_project.id, "title": "Hack"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_project_stats(self):
        Task.objects.create(project=self.project, title="A", status=Task.Status.DONE)
        Task.objects.create(project=self.project, title="B", status=Task.Status.TODO)
        Task.objects.create(project=self.project, title="C", status=Task.Status.TODO)

        response = self.client.get(reverse("project-stats", args=[self.project.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data, {"total": 3, "todo": 2, "in_progress": 0, "done": 1}
        )

    def test_search_tasks(self):
        Task.objects.create(project=self.project, title="Fix login bug")
        Task.objects.create(project=self.project, title="Update docs")
        response = self.client.get(reverse("task-list"), {"search": "login"})
        self.assertEqual(response.data["count"], 1)
