from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages


def login_view(request):
    return render(request, 'ccat_student/login.html')

def signup_step1(request):
    return render(request, 'ccat_student/signup_step1.html')