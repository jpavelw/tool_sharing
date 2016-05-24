from django.db import models
from manage_tools.models import Tool
from user.models import User


class Request(models.Model):
    PENDING_APPROVAL = 'PA'
    APPROVED = 'AP'
    REJECTED = 'RE'
    RETURNED = 'RT'

    status_choices = (
        (PENDING_APPROVAL, 'Pending Approval'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (RETURNED, 'Returned')
    )

    tool = models.ForeignKey(Tool, related_name='requests')
    lender = models.ForeignKey(User, related_name='lender_requests')
    borrower = models.ForeignKey(User, related_name='borrower_requests')
    status = models.CharField(choices=status_choices, max_length=2, default="PA")
    comment = models.CharField(max_length=150, default="")
    date = models.DateTimeField(auto_now_add=True, auto_now=False)
    returned_date = models.DateTimeField(null=True)
    shared_from = models.CharField(choices=Tool.shared_choices, max_length=2)
    zipcode = models.CharField(max_length=5)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    borrower_enabled = models.BooleanField(default=True)
    lender_enabled = models.BooleanField(default=True)
    may_leave_comment = models.BooleanField(default=False)

    def __str__(self):
        return self.status + " - " + str(self.tool.id) + " - " + str(self.lender.id) + " - " + str(self.borrower.id)

    def get_status_choices(self):
        return dict(self.status_choices).get(self.status)


class Notification(models.Model):
    user = models.OneToOneField(User)
    pending_sent = models.PositiveSmallIntegerField(default=0)
    pending_received = models.PositiveSmallIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return self.user.last_name + ", " + self.user.first_name

    def increment_sent(self):
        self.pending_sent += 1

    def increment_received(self):
        self.pending_received += 1
