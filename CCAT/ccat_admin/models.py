from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import uuid
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        # This fixes the display in the Django Admin sidebar
        verbose_name_plural = "Categories"

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
    question_image = models.ImageField(upload_to='question_images/', blank=True, null=True)
    num_options = models.PositiveSmallIntegerField(default=4)

    # The ID format you used in your UI (e.g., MATH-2024-001)
    custom_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.question_text[:50]

class Option(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    option_image = models.ImageField(upload_to='option_images/', blank=True, null=True)
    option_text = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.option_text} ({'Correct' if self.is_correct else 'Wrong'})"


class Student(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]

    PROGRAM_CHOICES = [
        ('bsit', 'Bachelor of Science in Information Technology'),
        ('bat', 'Bachelor of Agricultural Technology'),
        ('beed', 'Bachelor of Elementary Education'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')

    # --- Step 1: Personal Information ---
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_initial = models.CharField(max_length=5, blank=True, null=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    # --- Step 2: Contact Information ---
    mobile_number = models.CharField(max_length=20)
    alternative_contact = models.CharField(max_length=20, blank=True, null=True)

    # Address Fields
    street_address = models.CharField(max_length=255)
    barangay = models.CharField(max_length=100)
    city_municipality = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)

    # --- Step 3: Academic Background (NEW) ---
    last_school_attended = models.CharField(max_length=255)
    school_address = models.CharField(max_length=255)
    lrn_number = models.CharField(max_length=12)  # LRN is usually 12 digits
    gwa_score = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 99.99

    # --- Step 4: Course Preferences ---
    first_priority = models.CharField(max_length=10, choices=PROGRAM_CHOICES)
    second_priority = models.CharField(max_length=10, choices=PROGRAM_CHOICES)
    third_priority = models.CharField(max_length=10, choices=PROGRAM_CHOICES)

    # System Tracking
    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.first_priority}"

    def clean(self):
        super().clean()
        if self.first_priority and self.second_priority and self.third_priority:
            priorities = [self.first_priority, self.second_priority, self.third_priority]
            if len(set(priorities)) < 3:
                raise ValidationError("Please select three different courses for your priorities.")

class ExamResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    score_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=20)
    date_taken = models.DateTimeField(auto_now_add=True)
    total_correct = models.PositiveIntegerField(default=0)      # ADD
    total_questions = models.PositiveIntegerField(default=0)    # ADD
    breakdown = models.JSONField(default=dict)                  # ADD


class ExamConfig(models.Model):
    duration_minutes = models.PositiveIntegerField(default=120)
    randomize_questions = models.BooleanField(default=True)
    randomize_choices = models.BooleanField(default=True)
    tab_switch_deduction = models.PositiveIntegerField(default=10)

    class Meta:
        verbose_name = "Exam Configuration"

    def __str__(self):
        return f"Exam Config (duration={self.duration_minutes}m)"

    @classmethod
    def get_config(cls):
        """Always returns the single config row, creating it if it doesn't exist."""
        config, _ = cls.objects.get_or_create(pk=1)
        return config


class SessionKey(models.Model):
    session_name = models.CharField(max_length=100)
    # The unique code (e.g., ISU-A1B2)
    key_code = models.CharField(max_length=12, unique=True)

    # Capacity management
    capacity = models.PositiveIntegerField(default=50)
    used_count = models.PositiveIntegerField(default=0)

    # Expiration
    expiry_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Session Key"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.session_name} ({self.key_code})"

    @property
    def status(self):
        """Returns a string status for the UI badge."""
        if not self.is_active:
            return "Revoked"
        if timezone.now() > self.expiry_date:
            return "Expired"
        if self.used_count >= self.capacity:
            return "Full"
        return "Active"

    def is_valid(self):
        """Quick check if a student can use this key right now."""
        return (
                self.is_active and
                timezone.now() <= self.expiry_date and
                self.used_count < self.capacity
        )