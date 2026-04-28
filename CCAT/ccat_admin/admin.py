from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin


admin.site.site_header = "Super Admin"
admin.site.index_title = "Welcome to the Web-Based College Admission Test (WCAT)"

admin.site.unregister(Group)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),  # kept
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        # Groups and user_permissions fieldsets are simply omitted
    )

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)