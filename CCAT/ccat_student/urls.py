from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login_view'),
    path('signup/step-1/', views.signup_step1, name='signup_step1'),
    path('signup/step-2/', views.signup_step2, name='signup_step2'),
    path('signup/step-3/', views.signup_step3, name='signup_step3'),
    path('signup/step-4/', views.signup_step4, name='signup_step4'),
]