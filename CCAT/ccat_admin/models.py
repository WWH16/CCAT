from django.db import models
from django.contrib.auth.models import User


class AdminProfile(models.Model):
    ROLE_CHOICES = [
        ('REGISTRAR', 'Registrar'),
        ('DEPT_HEAD', 'Department Head'),
        ('SYSTEM_ADMIN', 'System Administrator'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='SYSTEM_ADMIN')
    employee_id = models.CharField(max_length=20, unique=True)
    campus = models.CharField(max_length=100, default="ISU Palanan Extension Campus")

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Category(models.Model):
    name = models.CharField(max_length=100)  # e.g., Mathematics, English

    def __str__(self):
        return self.name


class Question(models.Model):
    TYPE_CHOICES = [
        ('MCQ', 'Multiple Choice'),
        ('SS', 'Single Select'),
    ]

    question_text = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    question_type = models.CharField(max_length=5, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_validated = models.BooleanField(default=False)

    # The ID format you used in your UI (e.g., MATH-2024-001)
    custom_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.question_text[:50]

class Option(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    option_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.option_text} ({'Correct' if self.is_correct else 'Wrong'})"

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True) # ADM-2024-XXXX
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    department_applied = models.CharField(max_length=100)

class ExamResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    score_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=20) # Pass, Fail, In Progress
    date_taken = models.DateTimeField(auto_now_add=True)