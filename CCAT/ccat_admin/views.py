from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
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
                return render(request, 'ccat_admin/login.html', {'error': 'Access Denied'})
        else:
            return render(request, 'ccat_admin/login.html', {'error': 'Invalid credentials'})
    return render(request, 'ccat_admin/login.html')


def admin_logout(request):
    logout(request)
    return redirect('admin_login')


# --- Protected Admin Views ---
@login_required(login_url='admin_login')
def admin_dashboard(request):
    context = {
        'total_students': Student.objects.count(),
        'total_questions': Question.objects.count(),
        'passed_count': ExamResult.objects.filter(status='Pass').count(),
        'failed_count': ExamResult.objects.filter(status='Fail').count(),
        'recent_results': ExamResult.objects.select_related('student').order_by('-date_taken')[:5],
    }
    return render(request, 'ccat_admin/admin_dashboard.html', context)


@login_required(login_url='admin_login')
def question_management(request):
    if request.method == "POST":
        q_text = request.POST.get('text')
        cat_id = request.POST.get('category')
        q_type = request.POST.get('question_type')

        category = get_object_or_404(Category, id=cat_id)

        # Logic for custom ID (e.g., MATH-2026-001)
        count = Question.objects.filter(category=category).count() + 1
        custom_id = f"{category.name[:4].upper()}-2026-{count:03d}"

        new_q = Question.objects.create(
            question_text=q_text,
            category=category,
            question_type=q_type,
            custom_id=custom_id,
            is_validated=True
        )

        if q_type == 'MCQ':
            for letter in ['A', 'B', 'C', 'D']:
                opt_text = request.POST.get(f'option_{letter}')
                is_correct = (request.POST.get('correct_option') == letter)
                if opt_text:
                    Option.objects.create(question=new_q, option_text=opt_text, is_correct=is_correct)
        else:  # True/False (Layout sends 'SS')
            correct_val = request.POST.get('correct_tf')
            Option.objects.create(question=new_q, option_text="True", is_correct=(correct_val == "True"))
            Option.objects.create(question=new_q, option_text="False", is_correct=(correct_val == "False"))

        return redirect('question_management')

    # GET logic: select_related for category and prefetch_related for options
    # This prevents the "N+1" problem so your table loads fast
    questions = Question.objects.select_related('category').prefetch_related('options').all().order_by('-created_at')
    categories = Category.objects.all()

    return render(request, 'ccat_admin/question_management.html', {
        'questions': questions,
        'categories': categories
    })


@login_required(login_url='admin_login')
def exam_settings(request):
    return render(request, 'ccat_admin/exam_settings.html')