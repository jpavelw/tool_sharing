from django.db import models


class SharedZone(models.Model):
    name = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=5, unique=True)
    address = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return self.name
