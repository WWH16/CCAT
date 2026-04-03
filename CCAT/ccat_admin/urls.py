from django.urls import path
from . import views  # The dot '.' looks inside the current folder

urlpatterns = [
    # This maps the root of this app to your home view
    path('', views.admin_login, name='admin_login'),
    path('ccat_admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('ccat_admin/question_management/', views.question_management, name='question_management'),
    path('ccat_admin/exam_settings/', views.exam_settings, name='exam_settings'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('questions/export/', views.export_questions, name='export_questions'),
    path('ccat_admin/questions/<int:question_id>/edit/',   views.edit_question,   name='edit_question'),
    path('ccat_admin/questions/<int:question_id>/delete/', views.delete_question, name='delete_question'),
]