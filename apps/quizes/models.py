from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.programs.models import Program
from apps.applications.models import Application


class Subject(models.Model):
    """Test fanlari"""
    name = models.CharField(max_length=200, verbose_name="Fan nomi")
    code = models.CharField(max_length=20, unique=True, verbose_name="Fan kodi")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    
    class Meta:
        verbose_name = "Test fani"
        verbose_name_plural = "Test fanlari"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ProgramTest(models.Model):
    """Har bir yo'nalish uchun test sozlamalari"""
    program = models.OneToOneField(
        Program,
        on_delete=models.CASCADE,
        related_name="test_config",
        verbose_name="Yo'nalish"
    )
    subject_1 = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="program_tests_1",
        verbose_name="1-fan"
    )
    subject_2 = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="program_tests_2", 
        verbose_name="2-fan"
    )
    passing_score = models.IntegerField(
        default=55,
        verbose_name="O'tish balli"
    )
    time_limit = models.IntegerField(
        default=60,
        verbose_name="Vaqt chegarasi (daqiqa)"
    )
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    
    class Meta:
        verbose_name = "Yo'nalish test sozlamasi"
        verbose_name_plural = "Yo'nalish test sozlamalari"
    
    def __str__(self):
        return f"{self.program.name} - Test"


class Question(models.Model):
    """Test savollari"""
    SUBJECT_CHOICES = [
        ('subject_1', '1-fan'),
        ('subject_2', '2-fan'),
    ]
    
    program_test = models.ForeignKey(
        ProgramTest,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Yo'nalish testi"
    )
    subject_type = models.CharField(
        max_length=10,
        choices=SUBJECT_CHOICES,
        verbose_name="Fan turi"
    )
    question_number = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Savol raqami"
    )
    question_text = models.TextField(verbose_name="Savol matni")
    
    # Javob variantlari
    option_a = models.CharField(max_length=500, verbose_name="A variant")
    option_b = models.CharField(max_length=500, verbose_name="B variant")
    option_c = models.CharField(max_length=500, verbose_name="C variant")
    option_d = models.CharField(max_length=500, verbose_name="D variant")
    
    # To'g'ri javob
    correct_answer = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
        verbose_name="To'g'ri javob"
    )
    
    class Meta:
        verbose_name = "Test savoli"
        verbose_name_plural = "Test savollari"
        unique_together = ['program_test', 'subject_type', 'question_number']
        ordering = ['program_test', 'subject_type', 'question_number']
    
    def __str__(self):
        subject_name = self.get_subject_name()
        return f"{self.program_test.program.name} - {subject_name} - Savol {self.question_number}"
    
    def get_subject_name(self):
        if self.subject_type == 'subject_1':
            return self.program_test.subject_1.name
        else:
            return self.program_test.subject_2.name


class TestAttempt(models.Model):
    """Test urinishlari"""
    STATUS_CHOICES = [
        ('started', 'Boshlangan'),
        ('completed', 'Yakunlangan'),
        ('timed_out', 'Vaqt tugagan'),
    ]
    
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="test_attempts",
        verbose_name="Ariza"
    )
    program_test = models.ForeignKey(
        ProgramTest,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Yo'nalish testi"
    )
    attempt_number = models.IntegerField(default=1, verbose_name="Urinish raqami")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='started',
        verbose_name="Holat"
    )
    
    # Vaqt
    started_at = models.DateTimeField(default=timezone.now, verbose_name="Boshlangan")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Tugagan")
    time_spent = models.IntegerField(default=0, verbose_name="Vaqt (sekund)")
    
    # Har fan uchun natijalar
    subject_1_score = models.IntegerField(default=0, verbose_name="1-fan ball")
    subject_2_score = models.IntegerField(default=0, verbose_name="2-fan ball")
    
    # Umumiy natijalar
    total_score = models.IntegerField(default=0, verbose_name="Jami ball")
    percentage = models.FloatField(default=0.0, verbose_name="Foiz")
    is_passed = models.BooleanField(default=False, verbose_name="O'tdi")
    
    class Meta:
        verbose_name = "Test urinishi"
        verbose_name_plural = "Test urinishlari"
        ordering = ['-started_at']
        unique_together = ['application', 'program_test', 'attempt_number']
    
    def __str__(self):
        user_name = self.application.user.full_name or self.application.user.phone
        return f"{user_name} - {self.program_test.program.name} (#{self.attempt_number})"
    
    def calculate_results(self):
        """Natijalarni hisoblash"""
        # Har fan uchun to'g'ri javoblar sonini hisoblash
        subject_1_correct = self.answers.filter(
            question__subject_type='subject_1', 
            is_correct=True
        ).count()
        
        subject_2_correct = self.answers.filter(
            question__subject_type='subject_2', 
            is_correct=True
        ).count()
        
        # Har bir to'g'ri javob 5 ball
        self.subject_1_score = subject_1_correct * 5
        self.subject_2_score = subject_2_correct * 5
        self.total_score = self.subject_1_score + self.subject_2_score
        self.percentage = (self.total_score / 100) * 100
        self.is_passed = self.total_score >= self.program_test.passing_score
        
        self.save()


class Answer(models.Model):
    """Test javoblari"""
    attempt = models.ForeignKey(
        TestAttempt,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Test urinishi"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name="Savol"
    )
    selected_answer = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
        verbose_name="Tanlangan javob"
    )
    is_correct = models.BooleanField(verbose_name="To'g'ri")
    answered_at = models.DateTimeField(default=timezone.now, verbose_name="Javob vaqti")
    
    class Meta:
        verbose_name = "Test javobi"
        verbose_name_plural = "Test javoblari"
        unique_together = ['attempt', 'question']
        ordering = ['question__subject_type', 'question__question_number']
    
    def save(self, *args, **kwargs):
        # Javobning to'g'riligini tekshirish
        self.is_correct = self.selected_answer == self.question.correct_answer
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Q{self.question.question_number}: {self.selected_answer}"


class TestResult(models.Model):
    """Eng yaxshi test natijasi"""
    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name="test_result",
        verbose_name="Ariza"
    )
    best_attempt = models.ForeignKey(
        TestAttempt,
        on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name="Eng yaxshi urinish"
    )
    
    # Eng yaxshi natija
    best_total_score = models.IntegerField(default=0, verbose_name="Eng yaxshi ball")
    best_percentage = models.FloatField(default=0.0, verbose_name="Eng yaxshi foiz")
    is_test_passed = models.BooleanField(default=False, verbose_name="Test o'tdi")
    
    # Har fan uchun eng yaxshi ball
    best_subject_1_score = models.IntegerField(default=0, verbose_name="1-fan eng yaxshi")
    best_subject_2_score = models.IntegerField(default=0, verbose_name="2-fan eng yaxshi")
    
    # Statistika
    total_attempts = models.IntegerField(default=0, verbose_name="Jami urinishlar")
    last_attempt_date = models.DateTimeField(null=True, blank=True, verbose_name="Oxirgi urinish")
    
    class Meta:
        verbose_name = "Test natijasi"
        verbose_name_plural = "Test natijalari"
        ordering = ['-best_total_score']
    
    def update_best_result(self):
        """Eng yaxshi natijani yangilash"""
        best_attempt = self.application.test_attempts.filter(
            status='completed'
        ).order_by('-total_score').first()
        
        if best_attempt:
            self.best_attempt = best_attempt
            self.best_total_score = best_attempt.total_score
            self.best_percentage = best_attempt.percentage
            self.is_test_passed = best_attempt.is_passed
            self.best_subject_1_score = best_attempt.subject_1_score
            self.best_subject_2_score = best_attempt.subject_2_score
        
        self.total_attempts = self.application.test_attempts.count()
        if self.application.test_attempts.exists():
            self.last_attempt_date = self.application.test_attempts.order_by('-started_at').first().started_at
        
        self.save()
    
    def __str__(self):
        user_name = self.application.user.full_name or self.application.user.phone
        return f"{user_name} - Test: {self.best_total_score}/100"