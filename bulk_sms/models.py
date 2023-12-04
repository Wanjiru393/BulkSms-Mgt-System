from django.contrib.auth.models import User
from django.db import models
from datetime import datetime

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('approver', 'Approver'),
        ('non_approver', 'Non-Approver'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    staff_number = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=255)
    department = models.CharField(max_length=100)
    station = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='non_approver')


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=32)


class Customer(models.Model):
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    account_number = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class SMSTemplate(models.Model):
    content = models.TextField()
    issue_type = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class SMS(models.Model):
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    submission_date = models.DateTimeField(auto_now_add=True)
    approval_status = models.CharField(max_length=10, choices=APPROVAL_STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    issue_type = models.ForeignKey(SMSTemplate, on_delete=models.CASCADE)
    message_content = models.TextField()
    is_deleted = models.BooleanField(default=False)
    batch_number = models.CharField(max_length=12, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approved_sms')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) 
        if not self.batch_number:
            self.batch_number = datetime.now().strftime("%Y%m%d") + str(self.id)
            super().save(*args, **kwargs)