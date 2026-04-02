from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'ccat_admin/home.html')
def admin_dashboard(request):
    return render(request, 'ccat_admin/admin_dashboard.html')
def question_management(request):
    return render(request, 'ccat_admin/question_management.html')
def exam_settings(request):
    return render(request, 'ccat_admin/exam_settings.html')