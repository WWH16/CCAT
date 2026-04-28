from django.contrib import admin
from django.contrib.auth.models import Group
admin.site.unregister(Group)

admin.site.site_header = "Super Admin"
admin.site.index_title = "Welcome to the Web-Based College Admission Test (WCAT)"