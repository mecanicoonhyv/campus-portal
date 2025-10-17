from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, StudentProfile, FacultyProfile, StaffProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone', 'role', 'date_of_birth', 'address', 'city', 'state', 'zip_code')}),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'user', 'major', 'year_level', 'gpa', 'status']
    list_filter = ['status', 'year_level', 'major']
    search_fields = ['student_id', 'user__email', 'user__first_name', 'user__last_name']


@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    list_display = ['faculty_id', 'user', 'department', 'rank', 'status', 'is_professor']
    list_filter = ['status', 'rank', 'department', 'is_professor']
    search_fields = ['faculty_id', 'user__email', 'user__first_name', 'user__last_name']


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ['staff_id', 'user', 'department', 'position', 'status']
    list_filter = ['status', 'department']
    search_fields = ['staff_id', 'user__email', 'user__first_name', 'user__last_name']
