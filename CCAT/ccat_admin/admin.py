from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, Question, Option, Student, ExamResult, SessionKey, ExamConfig

# Customize the admin site headers and titles
admin.site.site_header = "ISU Palanan CCAT System"
admin.site.site_title = "ISU Palanan Admin"
admin.site.index_title = "System Administration"

admin.site.register(Category)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(Student)
admin.site.register(ExamResult)
admin.site.register(SessionKey)
admin.site.register(ExamConfig)