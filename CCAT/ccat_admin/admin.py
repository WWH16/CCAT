from django.contrib import admin
from django.contrib.auth.models import Group
admin.site.unregister(Group)

admin.site.site_header = "CCAT Admin Portal"
admin.site.index_title = "Welcome to the Computerized College Admission Test (CCAT) Admin Portal"