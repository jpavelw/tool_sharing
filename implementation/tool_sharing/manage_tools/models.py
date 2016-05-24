from django.db import models
from user.models import User


class ToolCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    enabled = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return self.name


class Tool(models.Model):
    AVAILABLE = 'AV'
    BORROWED = 'BR'
    RETURNED = 'RT'
    UNAVAILABLE = 'UA'
    status_choices = (
        (AVAILABLE, 'Available'),
        (BORROWED, 'Borrowed'),
        (RETURNED, 'Returned'),
        (UNAVAILABLE, 'Unavailable'),
    )
    editable_status_choices = (
        (AVAILABLE, 'Available'),
        (UNAVAILABLE, 'Unavailable'),
    )
    HOME = "HM"
    SHED = "SH"
    shared_choices = (
        (HOME, "Home"),
        (SHED, "Community Shed"),
    )
    name = models.CharField(max_length=100)
    status = models.CharField(choices=editable_status_choices, max_length=2, default="AV")
    owner = models.ForeignKey(User, related_name='tools', null=True, on_delete=models.SET_NULL)
    description = models.CharField(max_length=250)
    picture = models.FileField(upload_to="img/tools/", blank=True, default="img/tools/no-image.png")
    code = models.CharField(unique=True, max_length=10)
    shared_from = models.CharField(choices=shared_choices, max_length=2, default="HM")
    category = models.ForeignKey(ToolCategory, related_name='tools', null=True, on_delete=models.SET_NULL)
    enabled = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return self.code + " - " + self.name

    def is_shared_from_home(self):
        return self.shared_from == self.HOME

    def get_status_choices(self):
        return dict(self.status_choices).get(self.status)

    def get_shared_choices(self):
        return dict(self.shared_choices).get(self.shared_from)

    def get_all_shared_choices(self):
        return dict(self.shared_choices)


# this table store rate table for tool that rated by people
class ToolReview(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=150)
    rate = models.PositiveSmallIntegerField()
    user_name = models.CharField(max_length=20)
    user = models.ForeignKey(User)
    tool = models.ForeignKey(Tool)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return self.title + " - " + self.user_name
