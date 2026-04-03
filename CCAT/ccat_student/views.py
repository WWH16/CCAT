from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from ccat_admin.models import Student

def login_view(request):
    return render(request, 'ccat_student/login.html')

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
        p1, p2, p3 = request.POST.get('first_priority'), request.POST.get('second_priority'), request.POST.get('third_priority')

        if not all([p1, p2, p3]) or len({p1, p2, p3}) < 3:
            return render(request, 'ccat_student/signup_step4.html', {'error': 'Please select three unique priorities.'})

        username = data.get('lrn_number')
        if not username: return redirect('signup_step1')

        try:
            user = User.objects.create_user(username=username, password=username)
            Student.objects.create(
                user=user, **data,
                first_priority=p1, second_priority=p2, third_priority=p3
            )
            del request.session['signup_data']
            return render(request, 'ccat_student/success.html', {'lrn': username})
        except Exception as e:
            if 'user' in locals(): user.delete()
            return render(request, 'ccat_student/signup_step4.html', {'error': str(e)})
    return render(request, 'ccat_student/signup_step4.html')