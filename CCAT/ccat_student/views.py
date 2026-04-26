from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
import random
from django.utils import timezone
from django.contrib.auth import logout

from ccat_admin.models import Question, Category, Student, SessionKey, ExamConfig, Option, ExamResult


def signup_step1(request):
    if request.method == 'POST':
        request.session['signup_data'] = {
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'middle_initial': request.POST.get('middle_initial'),
            'date_of_birth': request.POST.get('date_of_birth'),
            'sex': request.POST.get('sex'),
        }
        return redirect('signup_step2')
    return render(request, 'ccat_student/signup_step1.html', {'form_data': request.session.get('signup_data', {})})

def signup_step2(request):
    if request.method == 'POST':
        data = request.session.get('signup_data', {})
        data.update({
            'mobile_number': request.POST.get('mobile_number'),
            'alternative_contact': request.POST.get('alternative_contact'),
            'email': request.POST.get('email'),
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
        lrn = request.POST.get('lrn_number')
        
        # Early check for duplicate LRN
        if User.objects.filter(username=lrn).exists():
            return render(request, 'ccat_student/signup_step3.html', {
                'error': 'This LRN is already registered. Please proceed to the login page.',
                'form_data': {
                    'lrn_number': lrn,
                    'last_school_attended': request.POST.get('last_school_attended'),
                    'school_address': request.POST.get('school_address'),
                    'track_strand': request.POST.get('track_strand'),
                }
            })

        data = request.session.get('signup_data', {})
        data.update({
            'lrn_number': lrn,
            'last_school_attended': request.POST.get('last_school_attended'),
            'school_address': request.POST.get('school_address'),
            'track_strand': request.POST.get('track_strand'),
        })
        request.session['signup_data'] = data
        return redirect('signup_step4')
    return render(request, 'ccat_student/signup_step3.html', {'form_data': request.session.get('signup_data', {})})


def signup_step4(request):
    data = request.session.get('signup_data', {})

    if request.method == 'POST':
        p1 = request.POST.get('first_priority')
        p2 = request.POST.get('second_priority')

        if not all([p1, p2]) or len({p1, p2}) < 2:
            return render(request, 'ccat_student/signup_step4.html', {
                'program_choices': Student.PROGRAM_CHOICES,
                'error': 'Please select two unique priorities.'
            })

        username = data.get('lrn_number')
        if not username:
            return redirect('signup_step1')

        try:
            user = User.objects.create_user(
                username=username, 
                password=username,
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                email=data.get('email', '')
            )
            
            # Create the Student profile
            Student.objects.create(
                user=user,
                **data,
                first_priority=p1,
                second_priority=p2
            )
            del request.session['signup_data']
            return render(request, 'ccat_student/success.html', {'lrn': username})

        except Exception as e:
            if 'user' in locals(): user.delete()
            return render(request, 'ccat_student/signup_step4.html', {
                'program_choices': Student.PROGRAM_CHOICES,
                'error': f"An error occurred: {str(e)}"
            })

    return render(request, 'ccat_student/signup_step4.html', {
        'program_choices': Student.PROGRAM_CHOICES,
    })


def login_view(request):
    if request.method == 'POST':
        lrn = request.POST.get('username')
        provided_key = request.POST.get('password')

        user = authenticate(request, username=lrn, password=lrn)

        if user is not None:
            try:
                session_key = SessionKey.objects.get(key_code=provided_key, is_active=True)

                if session_key.is_valid():
                    login(request, user)
                    return redirect('exam_instructions')
                else:
                    messages.error(request, f"Access Key is {session_key.status}.")

            except SessionKey.DoesNotExist:
                messages.error(request, "Invalid or Inactive Session Access Key.")
        else:
            messages.error(request, "Invalid LRN. Please check your registration.")

    return render(request, 'ccat_student/login.html')


def get_student(request):
    try:
        return request.user.student_profile
    except Student.DoesNotExist:
        return None


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


@login_required(login_url='login_view')
def exam_instructions(request):
    student = get_student(request)
    if not student:
        return redirect('login_view')

    # Handles case where user tries to access instructions after already taking the exam.
    if ExamResult.objects.filter(student=student).exists():
        return redirect('exam_result')

    config = ExamConfig.get_config()
    categories = Category.objects.filter(question__isnull=False).distinct()
    total_questions = Question.objects.count()
    total_sections = categories.count()

    active_session = SessionKey.objects.filter(is_active=True).first()
    session_name = active_session.session_name if active_session else "General Admission"

    # Join category names to display as exam coverage
    exam_coverage = ", ".join([cat.name for cat in categories]) if categories else "No categories defined"

    context = {
        'student': student,
        'config': config,
        'total_questions': total_questions,
        'total_sections': total_sections,
        'categorys': categories,
        'session_name': session_name,
        'exam_coverage': exam_coverage,
    }
    return render(request, 'ccat_student/exam_instructions.html', context)


def _build_exam_session(request, config):
    """
    Builds question/option order on first load, saves everything to session,
    and returns start_time directly so the caller doesn't need to re-read
    it from the session (which may not be flushed to disk yet).
    """
    categories = Category.objects.prefetch_related('question_set__options').all()
    question_id_order = []
    option_order_map  = {}
    sections          = []
    q_index           = 0

    for cat in categories:
        qs = list(cat.question_set.all())
        if not qs:
            continue

        if config.randomize_questions:
            random.shuffle(qs)

        for q in qs:
            opts = list(q.options.all())
            if config.randomize_choices:
                random.shuffle(opts)
            question_id_order.append(q.id)
            option_order_map[str(q.id)] = [o.id for o in opts]
            q_index += 1

        sections.append({
            'name': cat.name,
            'icon': get_icon(cat.name),
            'start': q_index - len(qs),
            'end': q_index - 1,
        })

    # Capture start_time as a local variable FIRST, then write to session.
    # We return it directly so exam_start doesn't have to re-read from session,
    # avoiding the file-session flush timing issue that caused the timer reset bug.
    start_time = timezone.now().timestamp()

    request.session['exam_question_order'] = question_id_order
    request.session['exam_option_order']   = option_order_map
    request.session['exam_sections']       = sections
    request.session['exam_answers']        = {}
    request.session['exam_flagged']        = []
    request.session['exam_start_time']     = start_time
    request.session.modified = True

    # Return start_time alongside the rest so caller uses the local value,
    # not a re-read from session which may not be persisted yet.
    return question_id_order, option_order_map, sections, start_time


@login_required(login_url='login_view')
def exam_start(request):
    student = get_student(request)
    if not student:
        return redirect('login_view')

    config = ExamConfig.get_config()

    # ── POST: score the exam ──────────────────────────────────────────────────
    if request.method == 'POST':
        if ExamResult.objects.filter(student=student).exists():
            return redirect('exam_result')

        question_id_order = request.session.get('exam_question_order', [])
        if not question_id_order:
            question_id_order = list(Question.objects.values_list('id', flat=True))

        questions = Question.objects.prefetch_related('options', 'category').filter(
            id__in=question_id_order
        )
        total     = len(question_id_order)
        correct   = 0
        breakdown = {}

        for q in questions:
            cat_name = q.category.name
            if cat_name not in breakdown:
                breakdown[cat_name] = {'correct': 0, 'total': 0}
            breakdown[cat_name]['total'] += 1

            submitted_option_id = request.POST.get(f'q_{q.id}')
            if submitted_option_id:
                try:
                    opt = Option.objects.get(id=submitted_option_id, question=q)
                    if opt.is_correct:
                        correct += 1
                        breakdown[cat_name]['correct'] += 1
                except Option.DoesNotExist:
                    pass

        ExamResult.objects.create(
            student=student,
            total_correct=correct,  # ADD
            total_questions=total,  # ADD
            breakdown=breakdown,  # ADD
        )

        for key in ['exam_question_order', 'exam_option_order', 'exam_sections',
                    'exam_answers', 'exam_flagged', 'exam_start_time']:
            request.session.pop(key, None)

        request.session['last_exam_breakdown']     = breakdown
        request.session['last_exam_total_correct'] = correct
        request.session['last_exam_total_q']       = total
        return redirect('exam_result')

    # ── GET: render the exam ──────────────────────────────────────────────────
    question_id_order = request.session.get('exam_question_order')
    if ExamResult.objects.filter(student=student).exists():
        return redirect('exam_result')
    option_order_map  = request.session.get('exam_option_order', {})
    sections          = request.session.get('exam_sections', [])
    saved_answers     = request.session.get('exam_answers', {})
    saved_flagged     = request.session.get('exam_flagged', [])

    if not question_id_order:
        # First load — _build_exam_session returns start_time directly.
        # We use that value instead of re-reading from session to avoid
        # the file-session flush timing bug.
        question_id_order, option_order_map, sections, start_time = _build_exam_session(request, config)
        saved_answers = {}
        saved_flagged = []
    else:
        # Subsequent loads (refresh) — session file is already written,
        # so reading exam_start_time is safe and correct here.
        start_time = request.session.get('exam_start_time')
        if start_time is None:
            # Safety fallback: session exists but start_time missing.
            # Treat as if exam just started (rare edge case).
            start_time = timezone.now().timestamp()
            request.session['exam_start_time'] = start_time
            request.session.modified = True

    # Calculate remaining seconds from server clock.
    # This always reflects reality regardless of how many times the page refreshes.
    elapsed           = timezone.now().timestamp() - start_time
    total_seconds     = config.duration_minutes * 60
    remaining_seconds = max(0, total_seconds - int(elapsed))

    question_map = {
        q.id: q
        for q in Question.objects.prefetch_related('options').filter(id__in=question_id_order)
    }

    all_questions = []
    for qid in question_id_order:
        q = question_map.get(qid)
        if not q:
            continue
        opt_ids = option_order_map.get(str(qid), [])
        opt_map = {o.id: o for o in q.options.all()}
        q.shuffled_options = [opt_map[oid] for oid in opt_ids if oid in opt_map]
        all_questions.append(q)

    resume_index     = 0
    flagged_indexes  = set(saved_flagged)
    answered_indexes = set()
    for i, q in enumerate(all_questions):
        if str(q.id) in saved_answers:
            answered_indexes.add(i)

    for i in range(len(all_questions)):
        if i in answered_indexes or i in flagged_indexes:
            resume_index = i + 1
        else:
            break
    resume_index = min(resume_index, len(all_questions) - 1)

    return render(request, 'ccat_student/exam.html', {
        'student': student,
        'config': config,
        'all_questions': all_questions,
        'sections': sections,
        'sections_json': json.dumps(sections),
        'total_questions': len(all_questions),
        'saved_answers_json': json.dumps(saved_answers),
        'saved_flagged_json': json.dumps(saved_flagged),
        'resume_index': resume_index,
        'remaining_seconds': remaining_seconds,
    })


# ── AJAX: save a single answer ────────────────────────────────────────────────

@require_POST
@login_required(login_url='login_view')
def exam_save_answer(request):
    try:
        data   = json.loads(request.body)
        q_id   = str(data.get('question_id'))
        opt_id = str(data.get('option_id'))

        if not q_id or not opt_id:
            return JsonResponse({'ok': False, 'error': 'Missing fields'}, status=400)

        answers       = request.session.get('exam_answers', {})
        answers[q_id] = opt_id
        request.session['exam_answers'] = answers
        request.session.modified = True

        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


# ── AJAX: toggle a flag ───────────────────────────────────────────────────────

@require_POST
@login_required(login_url='login_view')
def exam_save_flag(request):
    try:
        data       = json.loads(request.body)
        index      = int(data.get('index'))
        is_flagged = bool(data.get('flagged'))

        flagged = request.session.get('exam_flagged', [])
        if is_flagged and index not in flagged:
            flagged.append(index)
        elif not is_flagged and index in flagged:
            flagged.remove(index)

        request.session['exam_flagged'] = flagged
        request.session.modified = True

        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


# ── AJAX: apply a tab-switch penalty ─────────────────────────────────────────

@require_POST
@login_required(login_url='login_view')
def exam_apply_penalty(request):
    """
    Shifts exam_start_time backward by penalty_seconds.
    On next page load (or refresh), the server recalculates remaining time
    with the penalty already baked in — no periodic saves needed.
    """
    try:
        data            = json.loads(request.body)
        penalty_seconds = int(data.get('penalty_seconds', 0))

        if penalty_seconds <= 0:
            return JsonResponse({'ok': True})

        start_time = request.session.get('exam_start_time')
        if start_time is None:
            return JsonResponse({'ok': False, 'error': 'No active exam session'}, status=400)

        request.session['exam_start_time'] = start_time - penalty_seconds
        request.session.modified = True

        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


# ── Result & Logout ───────────────────────────────────────────────────────────

@login_required(login_url='login_view')
def exam_result(request):
    student = get_student(request)
    result = ExamResult.objects.filter(student=student).order_by('-date_taken').first()

    if not result:
        return redirect('exam_instructions')

    context = {
        'student': student,
        'result': result,
        'breakdown': result.breakdown,
        'total_correct': result.total_correct,
        'total_questions': result.total_questions,
    }
    return render(request, 'ccat_student/exam_result.html', context)


def logout_view(request):
    logout(request)
    return redirect('login_view')