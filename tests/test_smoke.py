import pytest
from django.test import SimpleTestCase
from django.urls import reverse

pytestmark = pytest.mark.functional


class ProjectSmokeTests(SimpleTestCase):
    def test_home_page_renders(self):
        response = self.client.get(reverse("home"))

        assert response.status_code == 200
        assert "Sistema de Gestión de Reservas Académicas" in response.content.decode()

