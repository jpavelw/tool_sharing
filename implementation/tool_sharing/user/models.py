from django.db import models
from utils.utilities import USStates
from shared_zone.models import SharedZone
from tool_sharing.settings import ADMIN_CODE


class Role(models.Model):

    ADMIN = "ADMIN"
    USER = "USER"
    role_choices = (
        (ADMIN, "Administrator"),
        (USER, "Regular user"),
    )

    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return self.name

    def get_role_choices(self, code):
        return dict(self.role_choices).get(code)

    def post_roles(self):
        try:
            role = Role()
            role.code = self.ADMIN
            role.name = self.get_role_choices(self.ADMIN)
            role.description = "Shared Zone coordinator."
            role.save()
        except:
            pass

        try:
            role = Role()
            role.code = self.USER
            role.name = self.get_role_choices(self.USER)
            role.description = "Shared Zone user."
            role.save()
        except:
            pass


class User(models.Model):
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    password = models.CharField(max_length=100)
    address = models.CharField(max_length=50)
    state = models.CharField(max_length=50, choices=USStates.states_list)
    city = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=5)
    shared_zone = models.ForeignKey(SharedZone, related_name='users', null=True, on_delete=models.SET_NULL)
    role = models.ForeignKey(Role, related_name='users', null=True, on_delete=models.SET_NULL)
    role_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    enabled = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    pickup_days = models.CharField(max_length=100, null=True)
    pickup_times = models.CharField(max_length=50, null=True)

    def is_admin(self):
        return self.role.code == ADMIN_CODE

    def get_address(self):
        return self.address + ". " + self.city + ", " + self.state

    def __str__(self):
        return self.last_name + ", " + self.first_name + " " + self.middle_name
