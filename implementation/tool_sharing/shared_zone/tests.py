from django.test import TestCase
from .models import SharedZone

# Create your tests here.

class ShareZoneTestCase(TestCase):
    def setUp(self):
        SharedZone.objects.create(zipcode="14623", name="Rebaz", description="hello world", address="214 alex road")

    def test_ShareZone1(self):
        test_ShareZone1 = SharedZone.objects.get(zipcode="14623")
        self.assertEqual(test_ShareZone1.name, "Rebaz")


class ShareZone2TestCase(TestCase):
    def setUp(self):
        SharedZone.objects.create(zipcode="12345", name="Rebaz", description="hello world", address="214 alex road")

    def test_ShareZone2(self):
        test_ShareZone2 = SharedZone.objects.get(zipcode="12345")
        self.assertNotEqual(test_ShareZone2.name, "wajdi")