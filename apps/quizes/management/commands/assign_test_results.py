from django.core.management.base import BaseCommand
from django.db import transaction
from apps.applications.models import Application, ApplicationStatus
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Barcha applicationlarga test natijalarini berish (55+ ball)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Bir vaqtda yangilanadigan applicationlar soni'
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        
        # Test ma'lumotlari yo'q applicationlar
        applications = Application.objects.filter(
            test_completed__isnull=True
        ).select_related('program')
        
        total_count = applications.count()
        self.stdout.write(f'Jami yangilanishi kerak: {total_count} ta application')
        
        if total_count == 0:
            self.stdout.write(self.style.SUCCESS('Barcha applicationlar allaqachon test natijasiga ega'))
            return
        
        updated_count = 0
        
        # Batch bo'lib yangilash
        for i in range(0, total_count, batch_size):
            batch = applications[i:i + batch_size]
            
            with transaction.atomic():
                for app in batch:
                    # Har doim 55+ ball berish
                    test_data = self.generate_passing_test_data(app)
                    
                    # Application yangilash
                    Application.objects.filter(id=app.id).update(**test_data)
                    updated_count += 1
            
            self.stdout.write(f'Yangilandi: {updated_count}/{total_count}')
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Jami {updated_count} ta application yangilandi')
        )
        self.stdout.write(
            self.style.SUCCESS('🎯 Barcha applicationlar 55+ ball bilan o\'tdi!')
        )

    def generate_passing_test_data(self, application):
        """Application uchun o'tadigan test ma'lumotlari (55+ ball)"""
        
        # 55 dan 100 gacha ball berish
        base_score = random.randint(55, 95)
        
        # Agar application qabul qilingan bo'lsa, yuqori ball berish
        if application.status == ApplicationStatus.ACCEPTED:
            base_score = random.randint(75, 100)
        elif application.status == ApplicationStatus.REVIEW:
            base_score = random.randint(65, 90)
        else:
            base_score = random.randint(55, 85)
        
        # Test sanasi (1-90 kun oldin)
        days_ago = random.randint(1, 90)
        test_date = timezone.now() - timedelta(days=days_ago)
        
        return {
            'test_completed': True,
            'test_score': base_score,
            'test_passed': True,  # Har doim True (55+ ball)
            'test_date': test_date
        }
