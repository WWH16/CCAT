from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Student, ExamResult, Question, Category, Option


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


@login_required(login_url='admin_login')
def question_management(request):
    if request.method == "POST":
        # 1. Get basic info
        q_text = request.POST.get('text')
        cat_id = request.POST.get('category')
        q_type = request.POST.get('question_type')

        # 2. Save the Question
        category = Category.objects.get(id=cat_id)
        # Create a unique ID (e.g., MATH-2026-001)
        count = Question.objects.filter(category=category).count() + 1
        custom_id = f"{category.name[:4].upper()}-2026-{count:03d}"

        new_q = Question.objects.create(
            question_text=q_text,
            category=category,
            question_type=q_type,
            custom_id=custom_id,
            is_validated=True  # Auto-validate for now
        )

        # 3. Save the Options based on type
        if q_type == 'MCQ':
            for letter in ['A', 'B', 'C', 'D']:
                opt_text = request.POST.get(f'option_{letter}')
                is_correct = (request.POST.get('correct_option') == letter)
                if opt_text:  # Only save if text exists
                    Option.objects.create(question=new_q, option_text=opt_text, is_correct=is_correct)
        else:  # True/False
            correct_val = request.POST.get('correct_tf')  # 'True' or 'False'
            Option.objects.create(question=new_q, option_text="True", is_correct=(correct_val == "True"))
            Option.objects.create(question=new_q, option_text="False", is_correct=(correct_val == "False"))

        return redirect('question_management')

    # GET: Load the page
    questions = Question.objects.select_related('category').all().order_by('-created_at')
    categories = Category.objects.all()
    return render(request, 'ccat_admin/question_management.html', {
        'questions': questions,
        'categories': categories
    })