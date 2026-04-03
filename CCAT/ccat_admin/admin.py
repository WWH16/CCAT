from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import AdminProfile, Category, Question, Option, Student, ExamResult, SessionKey

admin.site.register(AdminProfile)
admin.site.register(Category)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(Student)
admin.site.register(ExamResult)
admin.site.register(SessionKey)