from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class UserProfile(models.Model):
    """Extended user profile with registration request system"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    registration_requested = models.BooleanField(default=True)
    registration_approved = models.BooleanField(default=False)
    registration_request_date = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=200)
    
    def __str__(self):
        return f"{self.full_name} ({self.user.username}) - {'Approved' if self.registration_approved else 'Pending'}"

class Assignment(models.Model):
    Assignment_Name = models.CharField(max_length=500)
    Date = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        if self.Assignment_Name:
            return self.Assignment_Name
        return "Unnamed"
    
    def download_count(self):
        """Return the number of unique users who downloaded this assignment"""
        return self.downloads.filter(downloaded=True).values('user').distinct().count()


@receiver(post_save, sender=Assignment)
def send_assignment_notification(sender, instance, created, **kwargs):
    """Send email notification when a new assignment is created"""
    if created:  # Only send email for newly created assignments, not updates
        try:
            from Law_school.utils import send_assignment_notification_email
            send_assignment_notification_email(
                assignment_name=instance.Assignment_Name,
                assignment_date=instance.Date,
                assignment_description=instance.description or ""
            )
        except Exception as e:
            print(f"Error sending assignment notification email: {e}")
            # Continue even if email fails

class Download(models.Model):
    """Track user downloads of assignments"""
    # NOTE: user and assignment are temporarily nullable for migration from old model structure
    # After migration, delete old incompatible records, then make these fields non-nullable
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='downloads', null=True, blank=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='downloads', null=True, blank=True)
    downloaded = models.BooleanField(default=True)
    downloaded_at = models.DateTimeField(default=timezone.now)
    ip_address = models.CharField(max_length=100, blank=True, null=True)
    
    # Note: Meta class with unique_together will be added after cleaning old data
    # and making user/assignment fields non-nullable
    
    def __str__(self):
        if self.user and self.assignment:
            return f"{self.user.username} - {self.assignment.Assignment_Name} - Downloaded"
        return f"Old Download Record (ID: {self.id})"  # Temporary for old incompatible records

