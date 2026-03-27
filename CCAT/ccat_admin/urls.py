from django.urls import path
from . import views  # The dot '.' looks inside the current folder

urlpatterns = [
    # This maps the root of this app to your home view
    path('', views.home, name='home'),
]