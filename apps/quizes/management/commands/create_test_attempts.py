from django.core.management.base import BaseCommand
from django.db import transaction
from apps.applications.models import Application
from apps.quizes.models import TestResult, TestAttempt, ProgramTest
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Application ma\'lumotlari asosida TestAttempt va TestResult yaratish'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Bir vaqtda yaratilishi kerak bo\'lgan TestResult soni'
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        
        # Test completed=True lekin TestResult yo'q bo'lgan applicationlar
        applications = Application.objects.filter(
            test_completed=True,
            test_result__isnull=True
        ).select_related('program')
        
        total_count = applications.count()
        self.stdout.write(f'TestResult yaratish: {total_count} ta application')
        
        if total_count == 0:
            self.stdout.write(self.style.SUCCESS('Barcha applicationlar uchun TestResult mavjud'))
            return
        
        created_count = 0
        
        for i in range(0, total_count, batch_size):
            batch = applications[i:i + batch_size]
            
            with transaction.atomic():
                for app in batch:
                    try:
                        # TestAttempt yaratish
                        attempt = self.create_test_attempt(app)
                        
                        if attempt:
                            # TestResult yaratish
                            self.create_test_result(app, attempt)
                            created_count += 1
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Xatolik app {app.id}: {str(e)}')
                        )
            
            self.stdout.write(f'Yaratildi: {created_count}/{total_count}')
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Jami {created_count} ta TestResult yaratildi')
        )

    def create_test_attempt(self, application):
        """Application uchun TestAttempt yaratish"""
        
        # ProgramTest ni topish
        try:
            program_test = application.program.test_config
        except:
            self.stdout.write(
                self.style.WARNING(f'Program {application.program.name} uchun test config yo\'q')
            )
            return None
        
        # Ballni 2 ta fanga taqsim qilish (jami application.test_score)
        total_score = application.test_score or 55
        
        # Har bir fan maksimal 50 ball
        subject_1_score = random.randint(
            max(20, total_score - 50),  # Minimal 20, maksimal (total_score - 50)
            min(50, total_score - 5)    # Maksimal 50, minimal (total_score - 5)
        )
        subject_2_score = total_score - subject_1_score
        
        # subject_2_score ni ham cheklash
        if subject_2_score > 50:
            subject_2_score = 50
            subject_1_score = total_score - 50
        elif subject_2_score < 5:
            subject_2_score = 5
            subject_1_score = total_score - 5
        
        # Vaqt (30-90 daqiqa)
        time_spent = random.randint(1800, 5400)  # 30-90 daqiqa (soniyalarda)
        
        attempt = TestAttempt.objects.create(
            application=application,
            program_test=program_test,
            attempt_number=1,
            status='completed',
            started_at=application.test_date,
            completed_at=application.test_date + timezone.timedelta(seconds=time_spent),
            time_spent=time_spent,
            subject_1_score=subject_1_score,
            subject_2_score=subject_2_score,
            total_score=total_score,
            percentage=(total_score / 100) * 100,
            is_passed=True  # Har doim True (55+ ball)
        )
        
        return attempt

    def create_test_result(self, application, attempt):
        """Application uchun TestResult yaratish"""
        
        test_result = TestResult.objects.create(
            application=application,
            best_attempt=attempt,
            best_total_score=attempt.total_score,
            best_percentage=attempt.percentage,
            is_test_passed=True,  # Har doim True
            best_subject_1_score=attempt.subject_1_score,
            best_subject_2_score=attempt.subject_2_score,
            total_attempts=1,
            last_attempt_date=attempt.started_at
        )
        
        return test_result
