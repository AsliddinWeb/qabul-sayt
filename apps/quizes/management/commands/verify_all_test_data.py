from django.core.management.base import BaseCommand
from apps.applications.models import Application
from apps.quizes.models import TestResult, TestAttempt, ProgramTest, Subject, Question

class Command(BaseCommand):
    help = 'Barcha test ma\'lumotlarini tekshirish va statistika'

    def handle(self, *args, **options):
        self.stdout.write('=' * 60)
        self.stdout.write('TEST TIZIMI STATISTIKASI')
        self.stdout.write('=' * 60)
        
        # 1. Asosiy statistika
        self.show_basic_stats()
        
        # 2. Fanlar statistikasi
        self.show_subjects_stats()
        
        # 3. Test sozlamalari
        self.show_program_tests_stats()
        
        # 4. Savollar statistikasi
        self.show_questions_stats()
        
        # 5. Application test ma'lumotlari
        self.show_applications_stats()
        
        # 6. TestResult va TestAttempt
        self.show_test_results_stats()
        
        # 7. Xatoliklarni tekshirish
        self.check_errors()

    def show_basic_stats(self):
        """Asosiy statistika"""
        self.stdout.write('\n📊 ASOSIY STATISTIKA:')
        self.stdout.write('-' * 30)
        
        total_subjects = Subject.objects.count()
        active_subjects = Subject.objects.filter(is_active=True).count()
        total_program_tests = ProgramTest.objects.count()
        total_questions = Question.objects.count()
        
        self.stdout.write(f'Jami fanlar: {total_subjects} (faol: {active_subjects})')
        self.stdout.write(f'Program test sozlamalari: {total_program_tests}')
        self.stdout.write(f'Jami test savollari: {total_questions}')

    def show_subjects_stats(self):
        """Fanlar statistikasi"""
        self.stdout.write('\n📚 FANLAR:')
        self.stdout.write('-' * 30)
        
        subjects = Subject.objects.filter(is_active=True).order_by('name')
        for subject in subjects:
            used_count = ProgramTest.objects.filter(
                models.Q(subject_1=subject) | models.Q(subject_2=subject)
            ).count()
            self.stdout.write(f'• {subject.name} ({subject.code}): {used_count} ta programmada')

    def show_program_tests_stats(self):
        """Program test sozlamalari"""
        self.stdout.write('\n🎯 PROGRAM TEST SOZLAMALARI:')
        self.stdout.write('-' * 30)
        
        total_programs = ProgramTest.objects.count()
        programs_with_questions = ProgramTest.objects.filter(
            questions__isnull=False
        ).distinct().count()
        
        self.stdout.write(f'Test sozlamasi bor: {total_programs} ta program')
        self.stdout.write(f'Savollari bor: {programs_with_questions} ta program')

    def show_questions_stats(self):
        """Savollar statistikasi"""
        self.stdout.write('\n❓ SAVOLLAR:')
        self.stdout.write('-' * 30)
        
        total_questions = Question.objects.count()
        subject_1_questions = Question.objects.filter(subject_type='subject_1').count()
        subject_2_questions = Question.objects.filter(subject_type='subject_2').count()
        
        self.stdout.write(f'Jami savollar: {total_questions}')
        self.stdout.write(f'1-fan savollari: {subject_1_questions}')
        self.stdout.write(f'2-fan savollari: {subject_2_questions}')

    def show_applications_stats(self):
        """Application test ma'lumotlari"""
        self.stdout.write('\n📋 APPLICATION TEST MA\'LUMOTLARI:')
        self.stdout.write('-' * 30)
        
        total_apps = Application.objects.count()
        test_completed = Application.objects.filter(test_completed=True).count()
        test_passed = Application.objects.filter(test_passed=True).count()
        avg_score = Application.objects.filter(
            test_completed=True, test_score__isnull=False
        ).aggregate(avg_score=models.Avg('test_score'))['avg_score']
        
        self.stdout.write(f'Jami applicationlar: {total_apps}')
        self.stdout.write(f'Test topshirganlar: {test_completed}')
        self.stdout.write(f'Test o\'tganlar: {test_passed}')
        self.stdout.write(f'O\'rtacha ball: {avg_score:.1f}' if avg_score else 'O\'rtacha ball: N/A')

    def show_test_results_stats(self):
        """TestResult va TestAttempt statistikasi"""
        self.stdout.write('\n🏆 TEST NATIJALARI:')
        self.stdout.write('-' * 30)
        
        total_results = TestResult.objects.count()
        total_attempts = TestAttempt.objects.count()
        passed_results = TestResult.objects.filter(is_test_passed=True).count()
        
        self.stdout.write(f'TestResult mavjud: {total_results}')
        self.stdout.write(f'TestAttempt mavjud: {total_attempts}')
        self.stdout.write(f'Test o\'tgan natijalar: {passed_results}')

    def check_errors(self):
        """Xatoliklarni tekshirish"""
        self.stdout.write('\n🔍 XATOLIKLAR TEKSHIRUVI:')
        self.stdout.write('-' * 30)
        
        errors = []
        warnings = []
        
        # 1. Test completed=True lekin TestResult yo'q
        missing_results = Application.objects.filter(
            test_completed=True,
            test_result__isnull=True
        ).count()
        
        if missing_results > 0:
            errors.append(f'{missing_results} ta applicationda TestResult yo\'q')
        
        # 2. ProgramTest yo'q bo'lgan programlar
        from apps.programs.models import Program
        programs_without_test = Program.objects.filter(test_config__isnull=True).count()
        
        if programs_without_test > 0:
            warnings.append(f'{programs_without_test} ta programmada test sozlamasi yo\'q')
        
        # 3. Savollari yo'q ProgramTestlar
        tests_without_questions = ProgramTest.objects.filter(
            questions__isnull=True
        ).count()
        
        if tests_without_questions > 0:
            warnings.append(f'{tests_without_questions} ta test sozlamasida savollar yo\'q')
        
        # 4. Test score va TestResult nomuvofiqlik
        mismatched_scores = 0
        test_apps = Application.objects.filter(
            test_completed=True, test_result__isnull=False
        ).select_related('test_result')[:100]  # Birinchi 100 tasini tekshirish
        
        for app in test_apps:
            if app.test_score != app.test_result.best_total_score:
                mismatched_scores += 1
        
        if mismatched_scores > 0:
            warnings.append(f'{mismatched_scores} ta applicationda ball nomuvofiq (100 tasidan)')
        
        # Natijalarni chiqarish
        if not errors and not warnings:
            self.stdout.write(self.style.SUCCESS('✅ Hech qanday xatolik topilmadi!'))
        else:
            if errors:
                self.stdout.write(self.style.ERROR('❌ XATOLIKLAR:'))
                for error in errors:
                    self.stdout.write(self.style.ERROR(f'  • {error}'))
            
            if warnings:
                self.stdout.write(self.style.WARNING('⚠️ OGOHLANTIRISHLAR:'))
                for warning in warnings:
                    self.stdout.write(self.style.WARNING(f'  • {warning}'))
        
        self.stdout.write('\n' + '=' * 60)
