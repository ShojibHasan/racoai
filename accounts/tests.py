from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import TestCase

User = get_user_model()


class UserModelTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(email="a@example.com", password="secretpass")
        self.assertEqual(user.email, "a@example.com")
        self.assertTrue(user.check_password("secretpass"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        admin = User.objects.create_superuser(email="admin@example.com", password="secretpass")
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_email_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="secretpass")

    def test_email_normalized(self):
        user = User.objects.create_user(email="a@EXAMPLE.COM", password="secretpass")
        self.assertEqual(user.email, "a@example.com")

    def test_email_unique(self):
        User.objects.create_user(email="dup@example.com", password="secretpass")
        with self.assertRaises(IntegrityError):
            User.objects.create_user(email="dup@example.com", password="secretpass")

    def test_password_not_stored_raw(self):
        user = User.objects.create_user(email="b@example.com", password="secretpass")
        self.assertNotEqual(user.password, "secretpass")
