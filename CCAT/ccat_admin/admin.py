from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.models import User

from .models import ExamResult, Question, Option, Student, Category

# Customize the admin site headers and titles
admin.site.site_header = "ISU Palanan CCAT System"
admin.site.site_title = "ISU Palanan Admin"
admin.site.index_title = "System Administration"

# admin.site.register(ExamResult)