from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'ccat_admin/home.html')
def admin_dashboard(request):
    return render(request, 'ccat_admin/admin_dashboard.html')