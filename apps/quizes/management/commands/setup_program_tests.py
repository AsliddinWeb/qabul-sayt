from django.core.management.base import BaseCommand
from django.db import transaction
from apps.quizes.models import Subject, ProgramTest
from apps.programs.models import Program

class Command(BaseCommand):
    help = 'Har bir yo\'nalish uchun test sozlamalarini yaratish'

    def handle(self, *args, **options):
        self.stdout.write('Yo\'nalishlar uchun test sozlamalarini yaratish...')
        
        with transaction.atomic():
            programs = Program.objects.all()
            created_count = 0
            
            for program in programs:
                if hasattr(program, 'test_config'):
                    continue  # Allaqachon mavjud
                
                # Yo'nalishga qarab fanlarni tanlash
                subject1, subject2 = self.select_subjects_for_program(program)
                
                if subject1 and subject2:
                    test_config = ProgramTest.objects.create(
                        program=program,
                        subject_1=subject1,
                        subject_2=subject2,
                        passing_score=55,
                        time_limit=90,  # 90 daqiqa
                        max_attempts=3
                    )
                    created_count += 1
                    
                    self.stdout.write(f'✅ {program.name}: {subject1.name} + {subject2.name}')
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️ {program.name} uchun fan topilmadi')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(f'{created_count} ta test sozlamasi yaratildi')
            )

    def select_subjects_for_program(self, program):
        """Yo'nalishga qarab 2 ta fan tanlash"""
        program_name = program.name.lower()
        
        # Subject kodlarini olish
        try:
            # Matematika va O'zbek tili - default
            math = Subject.objects.get(code='MATH')
            uzb = Subject.objects.get(code='UZB')
            eng = Subject.objects.get(code='ENG')
            
            # Yo'nalishlarga qarab fanlarni tanlash
            if 'iqtisodiyot' in program_name:
                econ = Subject.objects.get(code='ECON_THEORY')
                return math, econ
            
            elif 'moliya' in program_name:
                finance = Subject.objects.get(code='FINANCE')
                return math, finance
            
            elif 'buxgalteriya' in program_name or 'audit' in program_name:
                accounting = Subject.objects.get(code='ACCOUNTING')
                return math, accounting
            
            elif 'axborot' in program_name or 'dasturiy' in program_name:
                programming = Subject.objects.get(code='PROGRAMMING')
                return math, programming
            
            elif 'ingliz' in program_name:
                eng_gram = Subject.objects.get(code='ENG_GRAM')
                return eng, eng_gram
            
            elif 'rus' in program_name:
                rus_gram = Subject.objects.get(code='RUS_GRAM')
                return uzb, rus_gram
            
            elif 'nemis' in program_name:
                ger_gram = Subject.objects.get(code='GER_GRAM')
                return eng, ger_gram
            
            elif 'o\'zbek' in program_name and 'til' in program_name:
                uzb_gram = Subject.objects.get(code='UZB_GRAM')
                lit = Subject.objects.get(code='LIT')
                return uzb_gram, lit
            
            elif 'pedagogika' in program_name and 'maxsus' in program_name:
                ped = Subject.objects.get(code='PED')
                special_ped = Subject.objects.get(code='SPECIAL_PED')
                return ped, special_ped
            
            elif 'pedagogika' in program_name:
                ped = Subject.objects.get(code='PED')
                psy = Subject.objects.get(code='PSY')
                return ped, psy
            
            elif 'maktabgacha' in program_name:
                preschool = Subject.objects.get(code='PRESCHOOL')
                psy = Subject.objects.get(code='PSY')
                return preschool, psy
            
            elif 'boshlang\'ich' in program_name:
                primary = Subject.objects.get(code='PRIMARY')
                ped = Subject.objects.get(code='PED')
                return primary, ped
            
            elif 'jismoniy' in program_name:
                pe_theory = Subject.objects.get(code='PE_THEORY')
                return pe_theory, uzb
            
            elif 'psixologiya' in program_name:
                psy = Subject.objects.get(code='PSY')
                ped = Subject.objects.get(code='PED')
                return psy, ped
            
            elif 'tarix' in program_name:
                hist = Subject.objects.get(code='HIST')
                return hist, uzb
            
            elif 'matematika' in program_name:
                physics = Subject.objects.get(code='PHYSICS')
                return math, physics
            
            elif 'jurnalistika' in program_name:
                journalism = Subject.objects.get(code='JOURNALISM')
                return journalism, uzb
            
            elif 'kutubxona' in program_name:
                library = Subject.objects.get(code='LIBRARY')
                return library, uzb
            
            elif 'musiqa' in program_name:
                music_theory = Subject.objects.get(code='MUSIC_THEORY')
                music_hist = Subject.objects.get(code='MUSIC_HIST')
                return music_theory, music_hist
            
            elif 'qurilish' in program_name or 'shahar' in program_name:
                materials = Subject.objects.get(code='MATERIALS')
                construction = Subject.objects.get(code='CONSTRUCTION')
                return math, materials
            
            elif 'yer kadastri' in program_name:
                geodesy = Subject.objects.get(code='GEODESY')
                return math, geodesy
            
            elif 'lingvistika' in program_name:
                ling = Subject.objects.get(code='LING')
                if 'ingliz' in program_name:
                    return eng, ling
                elif 'rus' in program_name:
                    return Subject.objects.get(code='RUS_GRAM'), ling
                elif 'nemis' in program_name:
                    return Subject.objects.get(code='GER_GRAM'), ling
                else:
                    return uzb, ling
            
            else:
                # Default: Matematika va O'zbek tili
                return math, uzb
                
        except Subject.DoesNotExist as e:
            self.stdout.write(
                self.style.ERROR(f'Fan topilmadi: {str(e)}')
            )
            return None, None
