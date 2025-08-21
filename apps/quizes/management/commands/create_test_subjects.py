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
                ("Matematika", "MATH", "Barcha yo'nalishlar uchun asosiy fan"),
                ("O'zbek tili va adabiyoti", "UZB", "Ona tili va adabiyot"),
                ("Ingliz tili", "ENG", "Chet tili"),
                ("Tarix", "HIST", "O'zbekiston va jahon tarixi"),
                ("Jismoniy tarbiya nazariyasi", "PE_THEORY", "Jismoniy tarbiya nazariy asoslari"),
                
                # Pedagogika fanlari
                ("Pedagogika asoslari", "PED", "Pedagogik faoliyat asoslari"),
                ("Psixologiya asoslari", "PSY", "Umumiy psixologiya"),
                ("Maktabgacha pedagogika", "PRESCHOOL", "Maktabgacha ta'lim"),
                ("Boshlang'ich ta'lim metodikasi", "PRIMARY", "Boshlang'ich sinf metodikasi"),
                ("Maxsus pedagogika", "SPECIAL_PED", "Maxsus ehtiyojli bolalar pedagogikasi"),
                
                # Filologiya fanlari
                ("O'zbek tili grammatikasi", "UZB_GRAM", "O'zbek tilining grammatik qoidalari"),
                ("Ingliz tili grammatikasi", "ENG_GRAM", "Ingliz tili grammatikasi"),
                ("Rus tili grammatikasi", "RUS_GRAM", "Rus tili grammatikasi"),
                ("Nemis tili grammatikasi", "GER_GRAM", "Nemis tili grammatikasi"),
                ("Adabiyotshunoslik", "LIT", "Adabiyot nazariyasi"),
                ("Tilshunoslik asoslari", "LING", "Umumiy tilshunoslik"),
                
                # Iqtisodiyot fanlari
                ("Iqtisodiyot nazariyasi", "ECON_THEORY", "Mikro va makroiqtisodiyot"),
                ("Buxgalteriya hisobi", "ACCOUNTING", "Buxgalteriya hisobi asoslari"),
                ("Moliya", "FINANCE", "Moliya va kredit"),
                ("Audit", "AUDIT", "Audit va nazorat"),
                ("Soliq va soliqqa tortish", "TAX", "Soliq tizimi"),
                
                # Axborot texnologiyalari
                ("Dasturlash asoslari", "PROGRAMMING", "Dasturlash tillari"),
                ("Ma'lumotlar bazasi", "DATABASE", "DBMS va SQL"),
                ("Kompyuter tarmoqlari", "NETWORKS", "Tarmoq texnologiyalari"),
                ("Axborot xavfsizligi", "INFO_SEC", "Kiberxavfsizlik"),
                ("Web texnologiyalar", "WEB_TECH", "Internet texnologiyalari"),
                
                # Qurilish va arxitektura
                ("Qurilish materiallari", "MATERIALS", "Qurilish materialshunoslik"),
                ("Arxitektura asoslari", "ARCH", "Arxitektura va dizayn"),
                ("Qurilish konstruksiyalari", "CONSTRUCTION", "Konstruksiyalar hisoblash"),
                ("Geodeziya", "GEODESY", "Yer o'lchash"),
                ("Shahar qurilishi", "URBAN", "Shaharsozlik"),
                
                # Musiqa va san'at
                ("Musiqa nazariyasi", "MUSIC_THEORY", "Musiqa nazariyasi asoslari"),
                ("Musiqa tarixi", "MUSIC_HIST", "Jahon musiqa tarixi"),
                ("Vokal pedagogikasi", "VOCAL", "Vokal o'qitish"),
                
                # Ommaviy kommunikatsiya
                ("Jurnalistika asoslari", "JOURNALISM", "OAV va jurnalistika"),
                ("Reklama va PR", "PR", "Jamoatchilik bilan aloqalar"),
                ("Media huquqi", "MEDIA_LAW", "OAV qonunchilik"),
                
                # Kutubxona ishi
                ("Kutubxonashunoslik", "LIBRARY", "Kutubxona ishi asoslari"),
                ("Bibliografiya", "BIBLIOGRAPHY", "Bibliografik ma'lumotnoma"),
                ("Arxivshunoslik", "ARCHIVE", "Arxiv ishi"),
                
                # Fan fanlari
                ("Fizika", "PHYSICS", "Umumiy fizika"),
                ("Kimyo", "CHEMISTRY", "Umumiy kimyo"),
                ("Biologiya", "BIOLOGY", "Umumiy biologiya"),
                ("Geografiya", "GEOGRAPHY", "Fizik va iqtisodiy geografiya"),
            ]
            
            created_count = 0
            for name, code, description in subjects_data:
                subject, created = Subject.objects.get_or_create(
                    code=code,
                    defaults={
                        'name': name,
                        'description': description,
                        'is_active': True
                    }
                )
                if created:
                    created_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'{created_count} ta yangi fan yaratildi')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Jami {Subject.objects.count()} ta fan mavjud')
            )
