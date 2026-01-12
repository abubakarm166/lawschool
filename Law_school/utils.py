"""
Utility functions for email notifications
"""
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from Law_school.models import UserProfile


def get_admin_emails():
    """Get all admin user emails"""
    admin_users = User.objects.filter(is_staff=True, is_active=True)
    return [admin.email for admin in admin_users if admin.email]


def send_registration_request_email_to_user(user_email, user_name):
    """Send confirmation email to user after registration request"""
    subject = 'Registration Request Submitted - Law School Portal'
    message = f"""
Hello {user_name},

Thank you for submitting your registration request to the Law School Portal.

Your registration request has been received and is pending administrator approval. 
You will receive another email once your request has been reviewed.

Please do not reply to this email.

Best regards,
Law School Portal
"""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email to user: {e}")
        return False


def send_registration_request_email_to_admin(user_email, user_name, username):
    """Send notification email to admin about new registration request"""
    admin_emails = get_admin_emails()
    if not admin_emails:
        print("No admin emails found. Please ensure at least one admin user has an email address.")
        return False
    
    subject = 'New Registration Request - Law School Portal'
    message = f"""
Hello Administrator,

A new registration request has been submitted:

Name: {user_name}
Username: {username}
Email: {user_email}

Please log in to the admin panel to review and approve/reject this request.

Admin Panel: {settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}/admin/

Best regards,
Law School Portal
"""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            admin_emails,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email to admin: {e}")
        return False


def send_assignment_notification_email(assignment_name, assignment_date, assignment_description=""):
    """Send notification email to all approved users when a new assignment is created"""
    approved_profiles = UserProfile.objects.filter(registration_approved=True)
    approved_users = [profile.user for profile in approved_profiles if profile.user.email and profile.user.is_active]
    
    if not approved_users:
        print("No approved users with email addresses found.")
        return False
    
    user_emails = [user.email for user in approved_users]
    
    subject = f'New Assignment Available: {assignment_name}'
    
    description_text = f"\nDescription: {assignment_description}\n" if assignment_description else ""
    
    message = f"""
Hello,

A new assignment has been added to the Law School Portal:

Assignment Name: {assignment_name}
Date/Deadline: {assignment_date}
{description_text}
Please log in to the portal to view and download the assignment.

Portal: {settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}/assignments/

Best regards,
Law School Portal
"""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            user_emails,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending assignment notification emails: {e}")
        return False
