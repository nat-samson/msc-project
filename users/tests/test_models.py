from django.test import TestCase

from users.models import User


class UserModelTests(TestCase):
    def test_student_str(self):
        # test __str__ for User model with a student instance
        user = User.objects.create_user(username='test_user', first_name='test', last_name='user', is_teacher=False)
        expected = 'test user (Student)'
        self.assertEqual(expected, str(user))

    def test_teacher_str(self):
        # test __str__ for User model with a teacher instance
        user = User.objects.create_user(username='test_user', first_name='test', last_name='user', is_teacher=True)
        expected = 'test user (Teacher)'
        self.assertEqual(expected, str(user))

    def test_admin_str(self):
        # test __str__ for User model with a teacher instance
        user = User.objects.create_superuser(username='test_user', first_name='test', last_name='user')
        expected = 'test user (Admin)'
        self.assertEqual(expected, str(user))
