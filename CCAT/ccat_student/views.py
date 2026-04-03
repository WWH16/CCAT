from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
import random
from django.utils import timezone

from ccat_admin.models import Question, Category, Student, SessionKey, ExamConfig, Option, ExamResult


def signup_step1(request):
    if request.method == 'POST':
        request.session['signup_data'] = {
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'middle_initial': request.POST.get('middle_initial'),
            'date_of_birth': request.POST.get('date_of_birth'),
            'gender': request.POST.get('gender'),
        }
        return redirect('signup_step2')
    return render(request, 'ccat_student/signup_step1.html', {'form_data': request.session.get('signup_data', {})})

def signup_step2(request):
    if request.method == 'POST':
        data = request.session.get('signup_data', {})
        data.update({
            'mobile_number': request.POST.get('mobile_number'),
            'alternative_contact': request.POST.get('alternative_contact'),
            'street_address': request.POST.get('street_address'),
            'barangay': request.POST.get('barangay'),
            'city_municipality': request.POST.get('city_municipality'),
            'province': request.POST.get('province'),
            'zip_code': request.POST.get('zip_code'),
        })
        request.session['signup_data'] = data
        return redirect('signup_step3')
    return render(request, 'ccat_student/signup_step2.html', {'form_data': request.session.get('signup_data', {})})

def signup_step3(request):
    if request.method == 'POST':
        data = request.session.get('signup_data', {})
        # Sync these keys with your HTML input names
        data.update({
            'lrn_number': request.POST.get('lrn_number'),
            'last_school_attended': request.POST.get('last_school_attended'),
            'school_address': request.POST.get('school_address'),
            'gwa_score': request.POST.get('gwa_score'),
        })
        request.session['signup_data'] = data
        return redirect('signup_step4')
    return render(request, 'ccat_student/signup_step3.html', {'form_data': request.session.get('signup_data', {})})


def signup_step4(request):
    data = request.session.get('signup_data', {})

    if request.method == 'POST':
        p1 = request.POST.get('first_priority')
        p2 = request.POST.get('second_priority')
        p3 = request.POST.get('third_priority')

        if not all([p1, p2, p3]) or len({p1, p2, p3}) < 3:
            return render(request, 'ccat_student/signup_step4.html',
                          {'error': 'Please select three unique priorities.'})

        username = data.get('lrn_number')
        if not username:
            return redirect('signup_step1')

        try:
            # CHANGE: Set password to 'username' (the LRN).
            # This allows the student to have an account, but they still
            # can't enter the exam without the Admin's SessionKey.
            user = User.objects.create_user(username=username, password=username)

            Student.objects.create(
                user=user,
                **data,
                first_priority=p1,
                second_priority=p2,
                third_priority=p3
            )

            del request.session['signup_data']

            # No need to show 'access_key' here since the Admin provides it later.
            return render(request, 'ccat_student/success.html', {'lrn': username})

        except Exception as e:
            if 'user' in locals(): user.delete()
            return render(request, 'ccat_student/signup_step4.html', {'error': str(e)})

    return render(request, 'ccat_student/signup_step4.html')


def login_view(request):
    if request.method == 'POST':
        lrn = request.POST.get('username')
        provided_key = request.POST.get('password')

        # 1. Authenticate the student account
        user = authenticate(request, username=lrn, password=lrn)

        if user is not None:
            try:
                # 2. Get the key from the database using actual fields
                session_key = SessionKey.objects.get(key_code=provided_key, is_active=True)

                # 3. Use your model's logic to check expiry and capacity
                if session_key.is_valid():
                    login(request, user)

                    # Optional: Increment the used_count since a student just logged in
                    session_key.used_count += 1
                    session_key.save()

                    return redirect('exam_instructions')
                else:
                    # Specific error based on why it's invalid
                    messages.error(request, f"Access Key is {session_key.status}.")

            except SessionKey.DoesNotExist:
                messages.error(request, "Invalid or Inactive Session Access Key.")
        else:
            messages.error(request, "Invalid LRN. Please check your registration.")

    return render(request, 'ccat_student/login.html')


@login_required(login_url='login_view')
def exam_instructions(request):
    student = get_student(request)
    if not student:
        return redirect('login_view')

    config = ExamConfig.get_config()

    # Get all categories that actually have questions
    # This matches the logic used in exam_start
    categories = Category.objects.filter(question__is_validated=True).distinct()

    total_questions = Question.objects.filter(is_validated=True).count()
    total_sections = categories.count()

    # Get the session name (optional: you could store the specific key used in request.session)
    active_session = SessionKey.objects.filter(is_active=True).first()
    session_name = active_session.session_name if active_session else "General Admission"

    context = {
        'student': student,
        'config': config,
        'total_questions': total_questions,
        'total_sections': total_sections,
        'categorys': categories,  # List of Category objects
        'session_name': session_name,
    }
    return render(request, 'ccat_student/exam_instructions.html', context)

def get_student(request):
    """Helper — gets the Student profile for the logged-in user."""
    try:
        return request.user.student_profile
    except Student.DoesNotExist:
        return None


# ── ICONS per category name (customize as needed)
CATEGORY_ICONS = {
    'mathematics': 'functions',
    'math': 'functions',
    'english': 'menu_book',
    'language': 'menu_book',
    'science': 'science',
    'general science': 'science',
    'reasoning': 'psychology',
    'logical reasoning': 'psychology',
}


def get_icon(category_name):
    return CATEGORY_ICONS.get(category_name.lower(), 'quiz')


@login_required(login_url='student_login')
def exam_start(request):
    """
    GET  — render the exam page with all questions loaded.
    POST — score answers and save ExamResult.
    """
    student = get_student(request)
    if not student:
        return redirect('student_login')

    config = ExamConfig.get_config()

    # ── POST: Score the submitted exam ──────────────────────────────────────
    if request.method == 'POST':
        questions = Question.objects.prefetch_related('options').all()
        total = questions.count()
        correct = 0

        for q in questions:
            submitted_option_id = request.POST.get(f'q_{q.id}')
            if submitted_option_id:
                try:
                    opt = Option.objects.get(id=submitted_option_id, question=q)
                    if opt.is_correct:
                        correct += 1
                except Option.DoesNotExist:
                    pass

        score_pct = round((correct / total) * 100, 2) if total > 0 else 0
        status = 'Pass' if score_pct >= 50 else 'Fail'

        ExamResult.objects.create(
            student=student,
            score_percentage=score_pct,
            status=status,
        )

        return redirect('exam_result')

    # ── GET: Build exam data ─────────────────────────────────────────────────
    # Fetch all questions grouped by category
    categories = Category.objects.prefetch_related('question_set__options').all()

    all_questions = []
    sections = []
    q_index = 0

    for cat in categories:
        qs = list(cat.question_set.prefetch_related('options').all())

        if not qs:
            continue

        if config.randomize_questions:
            random.shuffle(qs)

        if config.randomize_choices:
            for q in qs:
                q._shuffled_options = list(q.options.all())
                random.shuffle(q._shuffled_options)
            # Attach section index to each question for the template

        start_index = q_index
        for q in qs:
            q.section_index = len(sections)
            all_questions.append(q)
            q_index += 1

        sections.append({
            'name': cat.name,
            'icon': get_icon(cat.name),
            'start': start_index,
            'end': q_index - 1,
        })

    sections_json = json.dumps(sections)

    return render(request, 'ccat_student/exam.html', {
        'student': student,
        'config': config,
        'all_questions': all_questions,
        'sections': sections,
        'sections_json': sections_json,
        'total_questions': len(all_questions),
    })


@login_required(login_url='student_login')
def exam_result(request):
    student = get_student(request)
    if not student:
        return redirect('student_login')

    result = ExamResult.objects.filter(student=student).order_by('-date_taken').first()
    return render(request, 'ccat_student/exam_result.html', {
        'student': student,
        'result': result,
    })