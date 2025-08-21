# apps/quizes/management/commands/create_test_subjects.py

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.quizes.models import Subject

class Command(BaseCommand):
    help = 'Real yo\'nalishlar uchun test fanlarini yaratish'

    def handle(self, *args, **options):
        self.stdout.write('Test fanlarini yaratish...')
        
        with transaction.atomic():
            subjects_data = [
                # Umumiy fanlar
                ("Matematika", "MATH"),
                ("O'zbek tili va adabiyoti", "UZB"),
                ("Ingliz tili", "ENG"),
                ("Tarix", "HIST"),
                ("Jismoniy tarbiya nazariyasi", "PE_THEORY"),
                
                # Pedagogika fanlari
                ("Pedagogika asoslari", "PED"),
                ("Psixologiya asoslari", "PSY"),
                ("Maktabgacha pedagogika", "PRESCHOOL"),
                ("Boshlang'ich ta'lim metodikasi", "PRIMARY"),
                ("Maxsus pedagogika", "SPECIAL_PED"),
                
                # Filologiya fanlari
                ("O'zbek tili grammatikasi", "UZB_GRAM"),
                ("Ingliz tili grammatikasi", "ENG_GRAM"),
                ("Rus tili grammatikasi", "RUS_GRAM"),
                ("Nemis tili grammatikasi", "GER_GRAM"),
                ("Adabiyotshunoslik", "LIT"),
                ("Tilshunoslik asoslari", "LING"),
                
                # Iqtisodiyot fanlari
                ("Iqtisodiyot nazariyasi", "ECON_THEORY"),
                ("Buxgalteriya hisobi", "ACCOUNTING"),
                ("Moliya", "FINANCE"),
                ("Audit", "AUDIT"),
                ("Soliq va soliqqa tortish", "TAX"),
                
                # Axborot texnologiyalari
                ("Dasturlash asoslari", "PROGRAMMING"),
                ("Ma'lumotlar bazasi", "DATABASE"),
                ("Kompyuter tarmoqlari", "NETWORKS"),
                ("Axborot xavfsizligi", "INFO_SEC"),
                ("Web texnologiyalar", "WEB_TECH"),
                
                # Qurilish va arxitektura
                ("Qurilish materiallari", "MATERIALS"),
                ("Arxitektura asoslari", "ARCH"),
                ("Qurilish konstruksiyalari", "CONSTRUCTION"),
                ("Geodeziya", "GEODESY"),
                ("Shahar qurilishi", "URBAN"),
                
                # Musiqa va san'at
                ("Musiqa nazariyasi", "MUSIC_THEORY"),
                ("Musiqa tarixi", "MUSIC_HIST"),
                ("Vokal pedagogikasi", "VOCAL"),
                
                # Ommaviy kommunikatsiya
                ("Jurnalistika asoslari", "JOURNALISM"),
                ("Reklama va PR", "PR"),
                ("Media huquqi", "MEDIA_LAW"),
                
                # Kutubxona ishi
                ("Kutubxonashunoslik", "LIBRARY"),
                ("Bibliografiya", "BIBLIOGRAPHY"),
                ("Arxivshunoslik", "ARCHIVE"),
                
                # Fan fanlari
                ("Fizika", "PHYSICS"),
                ("Kimyo", "CHEMISTRY"),
                ("Biologiya", "BIOLOGY"),
                ("Geografiya", "GEOGRAPHY"),
            ]
            
            created_count = 0
            for name, code in subjects_data:
                subject, created = Subject.objects.get_or_create(
                    code=code,
                    defaults={
                        'name': name,
                        'is_active': True
                    }
                )
                if created:
                    created_count += 1
                    self.stdout.write(f'✅ Yaratildi: {name} ({code})')
                else:
                    self.stdout.write(f'⏭️ Mavjud: {name} ({code})')
            
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 {created_count} ta yangi fan yaratildi')
            )
            self.stdout.write(
                self.style.SUCCESS(f'📊 Jami {Subject.objects.count()} ta fan mavjud')
            )
