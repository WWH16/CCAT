from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Student, ExamResult, Question


# --- Authentication Views ---

def admin_login(request):
    if request.method == "POST":
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)

        if user is not None:
            if user.is_staff:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                return render(request, 'ccat_admin/login.html', {'error': 'Access Denied: Not an Administrator'})
        else:
            return render(request, 'ccat_admin/login.html', {'error': 'Invalid username or password'})

    return render(request, 'ccat_admin/login.html')


# --- Protected Admin Views ---

@login_required(login_url='admin_login')
def admin_dashboard(request):
    # Fetch real counts from the database
    total_students = Student.objects.count()
    total_questions = Question.objects.count()

    # Filter results by status
    passed_count = ExamResult.objects.filter(status='Pass').count()
    failed_count = ExamResult.objects.filter(status='Fail').count()

    # Get the 5 most recent exam results to show in a "Recent Activity" table
    recent_results = ExamResult.objects.select_related('student').order_by('-date_taken')[:5]

    context = {
        'total_students': total_students,
        'total_questions': total_questions,
        'passed_count': passed_count,
        'failed_count': failed_count,
        'recent_results': recent_results,
    }
    return render(request, 'ccat_admin/admin_dashboard.html', context)


@login_required(login_url='admin_login')
def question_management(request):
    # Fetch all questions to display in the repository
    questions = Question.objects.all().order_by('-created_at')
    return render(request, 'ccat_admin/question_management.html', {'questions': questions})


@login_required(login_url='admin_login')
def exam_settings(request):
    return render(request, 'ccat_admin/exam_settings.html')

def admin_logout(request):
    logout(request)
    return redirect('admin_login')