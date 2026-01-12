from django.contrib import admin
from Law_school.models import Assignment, Download, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'email', 'registration_approved', 'registration_request_date')
    list_filter = ('registration_approved', 'registration_request_date')
    search_fields = ('full_name', 'email', 'user__username')
    actions = ['approve_registrations', 'reject_registrations']
    
    def approve_registrations(self, request, queryset):
        """Admin action to approve registration requests"""
        count = queryset.update(registration_approved=True)
        self.message_user(request, f'{count} registration(s) approved successfully.')
    approve_registrations.short_description = "Approve selected registration requests"
    
    def reject_registrations(self, request, queryset):
        """Admin action to reject registration requests"""
        count = queryset.update(registration_approved=False)
        self.message_user(request, f'{count} registration(s) rejected.')
    reject_registrations.short_description = "Reject selected registration requests"


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('Assignment_Name', 'Date', 'created_at', 'download_count_display')
    list_filter = ('created_at',)
    search_fields = ('Assignment_Name', 'Date', 'description')
    
    def download_count_display(self, obj):
        """Display download count in admin"""
        count = obj.download_count()
        return f"{count} user(s)"
    download_count_display.short_description = "Downloads"


@admin.register(Download)
class DownloadAdmin(admin.ModelAdmin):
    list_display = ('user', 'assignment', 'downloaded_at', 'ip_address')
    list_filter = ('downloaded_at', 'assignment')
    search_fields = ('user__username', 'user__email', 'assignment__Assignment_Name')
    readonly_fields = ('downloaded_at',)
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'assignment')
