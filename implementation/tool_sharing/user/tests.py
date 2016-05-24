from django.test import TestCase
from .models import User, Role, SharedZone

class UserTestCase(TestCase):
    def setUp(self):
        User.objects.create(first_name="wajdi",
                            middle_name="mohammed",
                            last_name="aljedaani",
                            email="wajdi.j@hotmail.com",
                            password="123",
                            address="220 john street",
                            state="New York",
                            city="Rochester",
                            zipcode="14623")

    def testregister(self):
        testregister = User.objects.get(email="wajdi.j@hotmail.com")
        self.assertEqual(testregister.first_name, "wajdi")
        self.assertNotEqual(testregister.middle_name, "Jairo")


class LoginTestCase(TestCase):
    def setUp(self):
        User.objects.create(email="cap@mail.com", password="123")

    def testlogin(self):
        testlogin = User.objects.get(email="cap@mail.com")
        self.assertEqual(testlogin.password, "123")

class RoleTestCase(TestCase):
    def setUp(self):
        Role.objects.create(code="12", name="wajdi", description="hello world")

    def test_role(self):

        test_role = Role.objects.get(code="12")
        self.assertEqual(test_role.description, "hello world")

