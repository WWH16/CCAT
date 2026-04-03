from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    # path('signup/step-1/', views.signup_step1, name='signup_step1'),
    # path('signup/step-2/', views.signup_step2, name='signup_step2'),
    # Step 3 and 4 follow the same pattern...
]