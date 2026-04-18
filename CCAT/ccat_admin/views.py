from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Student, ExamResult, Question, Category, Option, ExamConfig, SessionKey
import csv, string, random
from django.utils import timezone
from django.http import HttpResponse
from django.utils.dateparse import parse_datetime # Add this import at the top
from django.core.paginator import Paginator
from django.db.models import Q, Count, Max
from django.http import JsonResponse


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

@login_required(login_url='admin_login')
def question_management(request):
    if request.method == "POST":
        q_text = request.POST.get('text')
        cat_id = request.POST.get('category')
        q_type = request.POST.get('question_type')

        category = get_object_or_404(Category, id=cat_id)

        # Logic for custom ID (e.g., MATH-001) — safe against deletions and Django admin inserts
        prefix = category.name[:4].upper()
        existing = Question.objects.filter(custom_id__startswith=f"{prefix}-").aggregate(Max('custom_id'))[
            'custom_id__max']
        last_num = int(existing.split('-')[-1]) if existing else 0
        custom_id = f"{prefix}-{last_num + 1:03d}"

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
    questions_list = Question.objects.select_related('category').prefetch_related('options').all().order_by(
        '-created_at')
    paginator = Paginator(questions_list, 20)  # 20 questions per page
    page_number = request.GET.get('page')
    questions = paginator.get_page(page_number)

    categories = Category.objects.all()

    return render(request, 'ccat_admin/question_management.html', {
        'questions': questions,
        'categories': categories
    })


@login_required(login_url='admin_login')
def exam_settings(request):
    config = ExamConfig.get_config()

    if request.method == 'POST':
        config.duration_minutes     = int(request.POST.get('duration_minutes', 120))
        config.randomize_questions  = 'randomize_questions' in request.POST
        config.randomize_choices    = 'randomize_choices' in request.POST
        config.tab_switch_deduction = int(request.POST.get('tab_switch_deduction', 10))
        config.save()
        return redirect('exam_settings')

    return render(request, 'ccat_admin/exam_settings.html', {
        'config':          config,
        'total_students':  Student.objects.count(),
        'total_questions': Question.objects.count(),
    })

@login_required(login_url='admin_login')
def export_questions(request):
    # Get current date in our region (UTC+8)
    # Using 'Asia/Singapore' is the reliable standard for PH time
    now = timezone.now().astimezone(timezone.get_current_timezone())

    # Clean Filename: ISU_Palanan_Questions_Apr-03-2026.csv
    date_str = now.strftime("%b-%d-%Y")
    filename = f"ISU_Palanan_Questions_{date_str}.csv"

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)

    # Official Header Section
    writer.writerow(['ISU PALANAN ADMISSION SYSTEM - QUESTION REPOSITORY'])
    writer.writerow(['Export Date:', now.strftime("%B %d, %Y")])
    writer.writerow([])  # Spacer

    # Table Headers
    writer.writerow(['ID', 'Question Text', 'Category', 'Type', 'Correct Answer', 'Date Created'])

    # Fetch data efficiently
    questions = Question.objects.select_related('category').prefetch_related('options').all().order_by('-created_at')

    for q in questions:
        # Get the correct answer
        correct_opt = q.options.filter(is_correct=True).first()
        answer_text = correct_opt.option_text if correct_opt else "N/A"

        # Clean text for CSV stability
        clean_text = q.question_text.replace('\n', ' ').replace('\r', '').strip()

        # Format the creation date of the question
        date_created = q.created_at.astimezone(timezone.get_current_timezone()).strftime("%m/%d/%Y")

        writer.writerow([
            q.custom_id,
            clean_text,
            q.category.name,
            q.get_question_type_display(),
            answer_text,
            date_created
        ])

    return response

@login_required(login_url='admin_login')
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        question.question_text = request.POST.get('text')
        question.category_id   = request.POST.get('category')
        question.question_type = request.POST.get('question_type')
        question.save()

        question.options.all().delete()

        if question.question_type == 'MCQ':
            correct_letter = request.POST.get('correct_option')
            for letter in ['A', 'B', 'C', 'D']:
                opt_text = request.POST.get(f'option_{letter}', '').strip()
                if opt_text:
                    Option.objects.create(question=question, option_text=opt_text, is_correct=(letter == correct_letter))
        else:
            correct_tf = request.POST.get('correct_tf')
            for label in ['True', 'False']:
                Option.objects.create(question=question, option_text=label, is_correct=(label == correct_tf))

    return redirect('question_management')


@login_required(login_url='admin_login')
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        question.delete()
    return redirect('question_management')


# Helper to generate the key
def generate_random_key():
    chars = string.ascii_uppercase + string.digits
    while True:
        # Format: ISU-XXXX
        code = f"ISU-{''.join(random.choices(chars, k=4))}"
        if not SessionKey.objects.filter(key_code=code).exists():
            return code


@login_required(login_url='admin_login')
def access_keys(request):
    keys = SessionKey.objects.all()
    # Check if any key is currently active to show/hide the yellow alert
    active_exists = keys.filter(is_active=True).exists()

    return render(request, 'ccat_admin/access_keys.html', {
        'session_keys': keys,
        'active_exists': active_exists
    })

@login_required(login_url='admin_login')
def generate_access_key(request):
    if request.method == "POST":
        session_name = request.POST.get('session_name')
        expiry_date_str = request.POST.get('expiry_date')

        # Convert the string to a timezone-aware datetime object
        naive_dt = parse_datetime(expiry_date_str)
        aware_dt = timezone.make_aware(naive_dt, timezone.get_current_timezone())

        # Policy: Deactivate all existing active keys first
        SessionKey.objects.filter(is_active=True).update(is_active=False)

        SessionKey.objects.create(
            session_name=session_name,
            key_code=generate_random_key(),
            expiry_date=aware_dt, # Use the aware datetime
            created_by=request.user,
            capacity=50
        )
    return redirect('access_keys')


@login_required(login_url='admin_login')
def revoke_key(request, key_id):
    key = get_object_or_404(SessionKey, id=key_id)
    key.is_active = False
    key.save()
    return redirect('access_keys')

# ── Dashboard ─────────────────────────────────────────────────────────────────

@login_required(login_url='admin_login')
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('admin_login')

    # ── Stat card counts ──────────────────────────────────────────────────────
    total_students = Student.objects.count()
    total_examinees = ExamResult.objects.values('student').distinct().count()
    passed_count = ExamResult.objects.filter(status='Pass').count()
    failed_count = ExamResult.objects.filter(status='Fail').count()
    # Get the currently active session key (if revoked or expired) to show in the admin panel
    active_session = SessionKey.objects.filter(is_active=True,expiry_date__gt=timezone.now()).first()

    # ── Search & filter ───────────────────────────────────────────────────────
    search = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()

    results = ExamResult.objects.select_related('student').order_by('-date_taken')

    if search:
        results = results.filter(
            Q(student__first_name__icontains=search) |
            Q(student__last_name__icontains=search)
        )

    if status_filter:
        results = results.filter(status=status_filter)

    # ── Pagination (20 per page) ───────────────────────────────────────────────
    paginator = Paginator(results, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'total_students': total_students,
        'total_examinees': total_examinees,
        'passed_count': passed_count,
        'failed_count': failed_count,
        'active_session': active_session,
        'page_obj': page_obj,
        # Preserve filter values so template can re-populate inputs and build pagination links
        'search': search,
        'status_filter': status_filter,
    }
    return render(request, 'ccat_admin/admin_dashboard.html', context)


# ── CSV Export ────────────────────────────────────────────────────────────────

@login_required(login_url='admin_login')
def admin_export_csv(request):
    """Export ALL exam results as a CSV file (ignores search/filter)."""
    if not request.user.is_staff:
        return redirect('admin_login')

    response = HttpResponse(content_type='text/csv')
    filename = f"exam_results_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)

    # Header row
    writer.writerow([
        'Last Name',
        'First Name',
        'Middle Initial',
        'LRN Number',
        'Gender',
        'Date of Birth',
        'Mobile Number',
        'Province',
        'City / Municipality',
        'Barangay',
        'Last School Attended',
        'GWA Score',
        'First Priority',
        'Second Priority',
        'Third Priority',
        'Score (%)',
        'Status',
        'Date Taken',
    ])

    results = (
        ExamResult.objects
        .select_related('student')
        .order_by('student__last_name', 'student__first_name')
    )

    for result in results:
        s = result.student
        writer.writerow([
            s.last_name,
            s.first_name,
            s.middle_initial or '',
            f'\t{s.lrn_number}',
            s.get_gender_display(),
            s.date_of_birth.strftime('%Y-%m-%d') if s.date_of_birth else '',
            f'\t{s.mobile_number}',
            s.province,
            s.city_municipality,
            s.barangay,
            s.last_school_attended,
            s.gwa_score,
            s.get_first_priority_display(),
            s.get_second_priority_display(),
            s.get_third_priority_display(),
            result.score_percentage,
            result.status,
            result.date_taken.strftime('%Y-%m-%d %H:%M:%S'),
        ])

    return response

@login_required(login_url='admin_login')
def category_add(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            return JsonResponse({'ok': False, 'error': 'Category name is required.'})
        if Category.objects.filter(name__iexact=name).exists():
            return JsonResponse({'ok': False, 'error': 'Category already exists.'})
        cat = Category.objects.create(name=name)
        return JsonResponse({'ok': True, 'id': cat.id, 'name': cat.name})
    return JsonResponse({'ok': False, 'error': 'Invalid request.'})


@login_required(login_url='admin_login')
def category_delete(request, category_id):
    if request.method == 'POST':
        cat = get_object_or_404(Category, id=category_id)
        if cat.question_set.exists():
            return JsonResponse({'ok': False, 'error': f'Cannot delete — "{cat.name}" has existing questions.'})
        cat.delete()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False, 'error': 'Invalid request.'})