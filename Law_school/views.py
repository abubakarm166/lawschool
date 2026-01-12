from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from Law_school.models import Assignment, Download, UserProfile
from Law_school.utils import send_registration_request_email_to_user, send_registration_request_email_to_admin
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotFound
import json

# Create your views here.

def index(request):
    """Home page - redirects to assignments if logged in, otherwise shows landing page"""
    if request.user.is_authenticated:
        # Check if user's registration is approved
        try:
            profile = request.user.profile
            if profile.registration_approved:
                return redirect('assignments_list')
            else:
                messages.info(request, 'Your registration request is pending approval by the administrator.')
                return render(request, 'pending_approval.html')
        except UserProfile.DoesNotExist:
            messages.error(request, 'Your profile is not set up. Please contact the administrator.')
            logout(request)
            return render(request, 'index.html')
    
    return render(request, 'index.html')

@csrf_exempt
def register_request(request):
    """Handle user registration requests"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        full_name = request.POST.get('full_name')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Validation
        if not all([username, email, full_name, password, password_confirm]):
            messages.error(request, 'All fields are required.')
            return render(request, 'register_request.html')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'register_request.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'register_request.html')
        
        if User.objects.filter(email=email).exists() or UserProfile.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'register_request.html')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Create profile with pending registration
        UserProfile.objects.create(
            user=user,
            email=email,
            full_name=full_name,
            registration_requested=True,
            registration_approved=False
        )
        
        # Send email notifications
        try:
            send_registration_request_email_to_user(email, full_name)
            send_registration_request_email_to_admin(email, full_name, username)
        except Exception as e:
            print(f"Error sending registration emails: {e}")
            # Continue even if email fails
        
        messages.success(request, 'Registration request submitted! Please wait for administrator approval. You should receive a confirmation email shortly.')
        return redirect('index')
    
    return render(request, 'register_request.html')

def user_login(request):
    """Handle user login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            try:
                profile = user.profile
                if profile.registration_approved:
                    login(request, user)
                    messages.success(request, f'Welcome back, {profile.full_name}!')
                    return redirect('assignments_list')
                else:
                    messages.warning(request, 'Your registration request is still pending approval.')
                    return render(request, 'login.html')
            except UserProfile.DoesNotExist:
                messages.error(request, 'Your profile is not set up. Please contact the administrator.')
                return render(request, 'login.html')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'login.html')
    
    return render(request, 'login.html')

@login_required
def user_logout(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('index')

@login_required
def assignments_list(request):
    """Display list of assignments for logged-in users"""
    # Check if user's registration is approved
    try:
        profile = request.user.profile
        if not profile.registration_approved:
            messages.warning(request, 'Your registration request is still pending approval.')
            return render(request, 'pending_approval.html')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Your profile is not set up. Please contact the administrator.')
        logout(request)
        return redirect('index')
    
    assignments = Assignment.objects.all().order_by('-created_at')
    context = {
        'assignments': assignments,
        'user_profile': profile
    }
    return render(request, 'assignments_list.html', context)

@csrf_exempt
@login_required
def download_assignment(request, assignment_id):
    """Handle assignment download tracking"""
    if request.method == 'POST':
        assignment = get_object_or_404(Assignment, id=assignment_id)
        
        # Check if user's registration is approved
        try:
            profile = request.user.profile
            if not profile.registration_approved:
                return JsonResponse({
                    'success': False,
                    'message': 'Your registration is not approved yet.'
                }, status=403)
        except UserProfile.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Your profile is not set up.'
            }, status=403)
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Create or update download record
        download, created = Download.objects.get_or_create(
            user=request.user,
            assignment=assignment,
            defaults={
                'downloaded': True,
                'ip_address': ip
            }
        )
        
        if not created:
            # Update existing record
            download.downloaded = True
            download.ip_address = ip
            download.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Download recorded successfully',
            'assignment_name': assignment.Assignment_Name
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=400)
