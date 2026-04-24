from django.contrib import admin
from .models import ExamResult

# Only register YOUR custom models
admin.site.register(ExamResult)

# Do NOT register User - it's already registered by Django