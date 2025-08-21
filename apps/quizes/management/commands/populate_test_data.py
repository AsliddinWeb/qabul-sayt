# apps/quizes/management/commands/populate_test_data.py

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.quizes.models import Subject, ProgramTest, Question
from apps.programs.models import Program
import random


class Command(BaseCommand):
    help = 'Quizes app ni to\'liq ma\'lumotlar bilan to\'ldirish'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Avval mavjud ma\'lumotlarni o\'chirish',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📚 Test ma\'lumotlarini yaratish boshlandi...'))

        if options['clear']:
            self.clear_existing_data()

        with transaction.atomic():
            # 1. Fanlarni yaratish
            subjects = self.create_subjects()
            self.stdout.write(f'✅ {len(subjects)} ta fan yaratildi')

            # 2. Har bir yo'nalish uchun test konfiguratsiyasi yaratish
            test_configs = self.create_test_configs(subjects)
            self.stdout.write(f'✅ {len(test_configs)} ta test konfiguratsiyasi yaratildi')

            # 3. Har bir test uchun savollar yaratish
            total_questions = self.create_questions(test_configs)
            self.stdout.write(f'✅ {total_questions} ta test savoli yaratildi')

        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 Barcha ma\'lumotlar muvaffaqiyatli yaratildi!\n'
                f'📊 Jami: {len(subjects)} fan, {len(test_configs)} test, {total_questions} savol'
            )
        )

    def clear_existing_data(self):
        """Mavjud ma'lumotlarni o'chirish"""
        self.stdout.write('🗑️ Mavjud ma\'lumotlarni o\'chirish...')
        Question.objects.all().delete()
        ProgramTest.objects.all().delete()
        Subject.objects.all().delete()
        self.stdout.write('✅ Eski ma\'lumotlar o\'chirildi')

    def create_subjects(self):
        """Fanlarni yaratish"""
        subjects_data = [
            # Asosiy fanlar
            ('Matematika', 'MATH'),
            ('Fizika', 'PHYS'),
            ('Kimyo', 'CHEM'),
            ('Biologiya', 'BIO'),
            ('Tarix', 'HIST'),
            ('Geografiya', 'GEO'),
            ('Adabiyot', 'LIT'),
            ('Ingliz tili', 'ENG'),
            ('Rus tili', 'RUS'),
            ('Nemis tili', 'GER'),
            ('O\'zbek tili', 'UZB'),
            
            # Ixtisoslik fanlar
            ('Iqtisodiyot nazariyasi', 'ECON'),
            ('Buxgalteriya hisobi', 'ACC'),
            ('Moliya', 'FIN'),
            ('Menejmenet', 'MGT'),
            ('Marketing', 'MKT'),
            ('Statistika', 'STAT'),
            ('Hukukshunoslik', 'LAW'),
            ('Psixologiya', 'PSY'),
            ('Pedagogika', 'PED'),
            ('Jurnalistika', 'JOUR'),
            ('Kutubxonashunoslik', 'LIB'),
            ('Axborot texnologiyalari', 'IT'),
            ('Dasturlash', 'PROG'),
            ('Ma\'lumotlar bazasi', 'DB'),
            ('Kompyuter grafikasi', 'CG'),
            ('Web dasturlash', 'WEB'),
            ('Qurilish materiallari', 'CM'),
            ('Arxitektura', 'ARCH'),
            ('Geodeziya', 'GEOD'),
            ('Yer kadastri', 'LAND'),
            ('Shahar qurilishi', 'URBAN'),
            ('Jismoniy tarbiya nazariyasi', 'PE'),
            ('Sport tibbi', 'SM'),
            ('Musiqa nazariyasi', 'MUS'),
            ('Musiqa tarixi', 'MHIST'),
            ('Maxsus pedagogika', 'SPED'),
            ('Logopediya', 'LOGO'),
            ('Boshlang\'ich ta\'lim metodikasi', 'PRIM'),
            ('Maktabgacha ta\'lim', 'PRE'),
            ('Til nazariyasi', 'LING'),
            ('Tarjima nazariyasi', 'TRANS'),
            ('Adabiyotshunoslik', 'LITST'),
            ('Mantiq', 'LOGIC'),
            ('Falsafa', 'PHIL'),
            ('Ijtimoiyshunoslik', 'SOC'),
            ('Siyosatshunoslik', 'POL'),
            ('Kulturashunoslik', 'CULT'),
            ('Etnoshunoslik', 'ETH'),
        ]

        subjects = []
        for name, code in subjects_data:
            subject, created = Subject.objects.get_or_create(
                code=code,
                defaults={'name': name, 'is_active': True}
            )
            subjects.append(subject)

        return subjects

    def create_test_configs(self, subjects):
        """Har bir yo'nalish uchun test konfiguratsiyasi yaratish"""
        # Fanlarni nom bo'yicha dict qilish
        subjects_dict = {subject.name: subject for subject in subjects}
        
        # Yo'nalish va fanlari mapping
        program_subjects = {
            # Iqtisodiyot yo'nalishlari
            'Iqtisodiyot': ('Matematika', 'Iqtisodiyot nazariyasi'),
            'Moliya va moliyaviy texnologiyalar': ('Matematika', 'Moliya'),
            'Buxgalteriya hisobi va audit': ('Matematika', 'Buxgalteriya hisobi'),
            
            # Filologiya yo'nalishlari
            'Filologiya va tillarni o\'qitish (o\'zbek tili)': ('O\'zbek tili', 'Adabiyot'),
            'Filologiya va tillarni o\'qitish (ingliz tili)': ('Ingliz tili', 'Til nazariyasi'),
            'Filologiya va tillarni o\'qitish (rus tili)': ('Rus tili', 'Til nazariyasi'),
            'Filologiya va tillarni o\'qitish (nemis tili)': ('Nemis tili', 'Til nazariyasi'),
            
            # Magistratura yo'nalishlari
            'Lingvistika (o\'zbek tili)': ('O\'zbek tili', 'Til nazariyasi'),
            'Lingvistika (ingliz tili)': ('Ingliz tili', 'Tarjima nazariyasi'),
            'Lingvistika (rus tili)': ('Rus tili', 'Tarjima nazariyasi'),
            'Lingvistika (nemis tili)': ('Nemis tili', 'Tarjima nazariyasi'),
            
            # Ta'lim yo'nalishlari
            'Pedagogika': ('Pedagogika', 'Psixologiya'),
            'Boshlang\'ich ta\'lim': ('Pedagogika', 'Boshlang\'ich ta\'lim metodikasi'),
            'Maktabgacha ta\'lim': ('Pedagogika', 'Maktabgacha ta\'lim'),
            'Maxsus pedagogika': ('Maxsus pedagogika', 'Psixologiya'),
            
            # IT yo'nalishlari
            'Axborot tizimlari va texnologiyalari': ('Matematika', 'Axborot texnologiyalari'),
            
            # Ijtimoiy fanlar
            'Psixologiya': ('Psixologiya', 'Biologiya'),
            'Tarix': ('Tarix', 'Geografiya'),
            'Jurnalistika': ('O\'zbek tili', 'Jurnalistika'),
            'Kutubxona-axborot faoliyati': ('O\'zbek tili', 'Kutubxonashunoslik'),
            
            # Sport va san'at
            'Jismoniy ma\'daniyat': ('Jismoniy tarbiya nazariyasi', 'Biologiya'),
            'Musiqa ta\'limi': ('Musiqa nazariyasi', 'Musiqa tarixi'),
            
            # Qurilish yo'nalishlari
            'Shahar qurilish hamda kommunal infratuzilmani tashkil etish va boshqarish': ('Matematika', 'Shahar qurilishi'),
            'Yer kadastri va yer qurish': ('Matematika', 'Yer kadastri'),
            
            # Aniq fanlar
            'Matematika': ('Matematika', 'Fizika'),
        }

        test_configs = []
        programs = Program.objects.all()

        for program in programs:
            # Yo'nalish nomini topish
            program_name_key = None
            for key in program_subjects.keys():
                if key in program.name:
                    program_name_key = key
                    break
            
            # Agar aniq mos kelmasa, umumiy fanlarni berish
            if not program_name_key:
                if 'Iqtisodiyot' in program.name or 'Moliya' in program.name or 'Buxgalteriya' in program.name:
                    subject1_name, subject2_name = 'Matematika', 'Iqtisodiyot nazariyasi'
                elif any(til in program.name for til in ['ingliz', 'rus', 'nemis', 'o\'zbek']):
                    subject1_name, subject2_name = 'O\'zbek tili', 'Til nazariyasi'
                elif 'ta\'lim' in program.name.lower() or 'Pedagogika' in program.name:
                    subject1_name, subject2_name = 'Pedagogika', 'Psixologiya'
                else:
                    subject1_name, subject2_name = 'Matematika', 'Fizika'
            else:
                subject1_name, subject2_name = program_subjects[program_name_key]

            # Fanlarni topish
            subject1 = subjects_dict.get(subject1_name)
            subject2 = subjects_dict.get(subject2_name)

            if subject1 and subject2:
                test_config, created = ProgramTest.objects.get_or_create(
                    program=program,
                    defaults={
                        'subject_1': subject1,
                        'subject_2': subject2,
                        'passing_score': 55,
                        'time_limit': 60,
                        'is_active': True
                    }
                )
                test_configs.append(test_config)

        return test_configs

    def create_questions(self, test_configs):
        """Har bir test uchun savollar yaratish"""
        total_questions = 0

        # Har bir yo'nalish uchun savollar ma'lumotlari
        questions_data = self.get_questions_data()

        for test_config in test_configs:
            # Subject 1 uchun 10 ta savol
            subject1_questions = self.get_subject_questions(
                test_config.subject_1.name, questions_data
            )
            for i, question_data in enumerate(subject1_questions[:10], 1):
                Question.objects.get_or_create(
                    program_test=test_config,
                    subject_type='subject_1',
                    question_number=i,
                    defaults=question_data
                )
                total_questions += 1

            # Subject 2 uchun 10 ta savol
            subject2_questions = self.get_subject_questions(
                test_config.subject_2.name, questions_data
            )
            for i, question_data in enumerate(subject2_questions[:10], 1):
                Question.objects.get_or_create(
                    program_test=test_config,
                    subject_type='subject_2',
                    question_number=i,
                    defaults=question_data
                )
                total_questions += 1

        return total_questions

    def get_subject_questions(self, subject_name, questions_data):
        """Ma'lum fan uchun savollarni qaytarish"""
        if subject_name in questions_data:
            return questions_data[subject_name]
        else:
            # Umumiy savollar
            return questions_data.get('Umumiy', [])

    def get_questions_data(self):
        """Barcha fanlar uchun test savollari"""
        return {
            'Matematika': [
                {
                    'question_text': '2x + 5 = 11 tenglamaning yechimi nechaga teng?',
                    'option_a': 'x = 2',
                    'option_b': 'x = 3',
                    'option_c': 'x = 4',
                    'option_d': 'x = 5',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Sin(30°) ning qiymati nechaga teng?',
                    'option_a': '1/2',
                    'option_b': '√2/2',
                    'option_c': '√3/2',
                    'option_d': '1',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'Kvadrat funksiya y = x² + 4x + 3 ning uchi qayerda joylashgan?',
                    'option_a': '(-2, -1)',
                    'option_b': '(-2, 1)',
                    'option_c': '(2, -1)',
                    'option_d': '(2, 1)',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'log₂(8) ning qiymati nechaga teng?',
                    'option_a': '2',
                    'option_b': '3',
                    'option_c': '4',
                    'option_d': '8',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Uchburchakning ichki burchaklari yig\'indisi necha gradus?',
                    'option_a': '90°',
                    'option_b': '180°',
                    'option_c': '270°',
                    'option_d': '360°',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Faktorial 5! ning qiymati nechaga teng?',
                    'option_a': '60',
                    'option_b': '100',
                    'option_c': '120',
                    'option_d': '150',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'Doira yuzi formulasi qanday?',
                    'option_a': 'πr',
                    'option_b': '2πr',
                    'option_c': 'πr²',
                    'option_d': '2πr²',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'Cos(60°) ning qiymati nechaga teng?',
                    'option_a': '1/2',
                    'option_b': '√2/2',
                    'option_c': '√3/2',
                    'option_d': '1',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'Progressiya: 2, 6, 18, 54, ... keyingi sonni toping',
                    'option_a': '108',
                    'option_b': '162',
                    'option_c': '216',
                    'option_d': '324',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Limit lim(x→0) sin(x)/x ning qiymati nechaga teng?',
                    'option_a': '0',
                    'option_b': '1',
                    'option_c': '∞',
                    'option_d': 'Mavjud emas',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'f(x) = x³ funksiyaning hosilasi qanday?',
                    'option_a': '3x²',
                    'option_b': 'x²',
                    'option_c': '3x',
                    'option_d': 'x³/3',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'Determinant |2 3; 1 4| ning qiymati nechaga teng?',
                    'option_a': '5',
                    'option_b': '8',
                    'option_c': '11',
                    'option_d': '14',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'e sonining taqribiy qiymati nechaga teng?',
                    'option_a': '2.71',
                    'option_b': '3.14',
                    'option_c': '1.41',
                    'option_d': '1.73',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'Kompleks son i² ning qiymati nechaga teng?',
                    'option_a': '1',
                    'option_b': '-1',
                    'option_c': 'i',
                    'option_d': '-i',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Integral ∫x dx ning qiymati qanday?',
                    'option_a': 'x² + C',
                    'option_b': 'x²/2 + C',
                    'option_c': '2x + C',
                    'option_d': 'x + C',
                    'correct_answer': 'B'
                }
            ],
            
            'Fizika': [
                {
                    'question_text': 'Yorug\'lik tezligi vakuumda necha m/s?',
                    'option_a': '3×10⁶ m/s',
                    'option_b': '3×10⁷ m/s',
                    'option_c': '3×10⁸ m/s',
                    'option_d': '3×10⁹ m/s',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'Nyutonning birinchi qonuni nima?',
                    'option_a': 'F = ma',
                    'option_b': 'Inersiya qonuni',
                    'option_c': 'Ta\'sir va aks ta\'sir qonuni',
                    'option_d': 'Gravitatsiya qonuni',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Elektr zaryadi birligi nima?',
                    'option_a': 'Amper',
                    'option_b': 'Volt',
                    'option_c': 'Kulon',
                    'option_d': 'Om',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'Gazning ideal holatida molekulalarning o\'rtacha kinetik energiyasi nimaga bog\'liq?',
                    'option_a': 'Bosimga',
                    'option_b': 'Hajmga',
                    'option_c': 'Temperaturaga',
                    'option_d': 'Zichlikka',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'Tovush tezligi havodagi 20°C da necha m/s?',
                    'option_a': '300 m/s',
                    'option_b': '330 m/s',
                    'option_c': '343 m/s',
                    'option_d': '350 m/s',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'Elektromagnit to\'lqinning chastotasi va to\'lqin uzunligi orasidagi bog\'lanish formulasi qanday?',
                    'option_a': 'c = λf',
                    'option_b': 'c = λ/f',
                    'option_c': 'c = f/λ',
                    'option_d': 'c = λ + f',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'Ohm qonuni formulasi qanday?',
                    'option_a': 'U = IR',
                    'option_b': 'I = UR',
                    'option_c': 'R = UI',
                    'option_d': 'P = UI',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'Planetonning II qonuni nima haqida?',
                    'option_a': 'Planetalar ellips bo\'ylab harakat qiladi',
                    'option_b': 'Sektorlar qonuni',
                    'option_c': 'Harmonik qonun',
                    'option_d': 'Gravitatsiya qonuni',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Termodinamikaning birinchi qonuni qanday ifodalanadi?',
                    'option_a': 'Q = U + A',
                    'option_b': 'Q = U - A',
                    'option_c': 'Q = A - U',
                    'option_d': 'Q = UA',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'Fotonning energiyasi formulasi qanday?',
                    'option_a': 'E = mc²',
                    'option_b': 'E = hf',
                    'option_c': 'E = mv²/2',
                    'option_d': 'E = mgh',
                    'correct_answer': 'B'
                }
            ],
            
            'Kimyo': [
                {
                    'question_text': 'Suvning kimyoviy formulasi qanday?',
                    'option_a': 'HO',
                    'option_b': 'H₂O',
                    'option_c': 'H₂O₂',
                    'option_d': 'HO₂',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Mendeleev davriy sistemasida nechta davr bor?',
                    'option_a': '6',
                    'option_b': '7',
                    'option_c': '8',
                    'option_d': '9',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Uglerodning atom raqami nechaga teng?',
                    'option_a': '4',
                    'option_b': '5',
                    'option_c': '6',
                    'option_d': '7',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'pH = 7 bo\'lgan eritmalar qanday xususiyatga ega?',
                    'option_a': 'Kislotali',
                    'option_b': 'Ishqoriy',
                    'option_c': 'Neytral',
                    'option_d': 'Indikator',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'Avogadro sonining qiymati nechaga teng?',
                    'option_a': '6.02×10²³',
                    'option_b': '6.02×10²²',
                    'option_c': '6.02×10²⁴',
                    'option_d': '3.14×10²³',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'Metallarning umumiy xususiyati qaysi?',
                    'option_a': 'Elektr o\'tkazmaydi',
                    'option_b': 'Issiqlik o\'tkazmaydi',
                    'option_c': 'Elektr o\'tkazadi',
                    'option_d': 'Hamma gazsimon',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'Organik kimyoning asosiy elementi qaysi?',
                    'option_a': 'Vodorod',
                    'option_b': 'Kislorod',
                    'option_c': 'Uglerod',
                    'option_d': 'Azot',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'Oksidlanish jarayonida nima sodir bo\'ladi?',
                    'option_a': 'Elektron qabul qiladi',
                    'option_b': 'Elektron beradi',
                    'option_c': 'Neytral qoladi',
                    'option_d': 'Yadro o\'zgaradi',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'NaCl (osh tuzi) qanday bog\'lanishga ega?',
                    'option_a': 'Kovalent',
                    'option_b': 'Ion',
                    'option_c': 'Metall',
                    'option_d': 'Van der Vaals',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Katalizator nima qiladi?',
                    'option_a': 'Reaksiya tezligini oshiradi',
                    'option_b': 'Reaksiya tezligini kamaytiradi',
                    'option_c': 'Mahsulotni o\'zgartiradi',
                    'option_d': 'Energiya ishlab chiqaradi',
                    'correct_answer': 'A'
                }
            ],
            
            'Biologiya': [
                {
                    'question_text': 'DNK ning to\'liq nomi nima?',
                    'option_a': 'Dezoksiribonuklein kislota',
                    'option_b': 'Ribonuklein kislota',
                    'option_c': 'Amino kislota',
                    'option_d': 'Nukleotid kislota',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'Fotosintez jarayoni qayerda sodir bo\'ladi?',
                    'option_a': 'Mitoxondriyada',
                    'option_b': 'Xloroplastda',
                    'option_c': 'Yadroda',
                    'option_d': 'Ribosomada',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Inson tanasida nechta suyak bor?',
                    'option_a': '206',
                    'option_b': '208',
                    'option_c': '210',
                    'option_d': '212',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'Qon aylanish tizimining asosiy vazifasi nima?',
                    'option_a': 'Ovqat hazm qilish',
                    'option_b': 'Nafas olish',
                    'option_c': 'Moddalar transporti',
                    'option_d': 'Harakat',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'Meioz natijasida nechta hujayra hosil bo\'ladi?',
                    'option_a': '2',
                    'option_b': '4',
                    'option_c': '6',
                    'option_d': '8',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Insulin gormoni qaysi organda ishlab chiqariladi?',
                    'option_a': 'Jigar',
                    'option_b': 'Buyrak',
                    'option_c': 'Oshqozon osti bezi',
                    'option_d': 'Qalqonsimon bez',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'Evolyutsiya nazariyasining asoschisi kim?',
                    'option_a': 'Mendel',
                    'option_b': 'Darwin',
                    'option_c': 'Pasteur',
                    'option_d': 'Fleming',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'ATP ning to\'liq nomi nima?',
                    'option_a': 'Adenozin trifosfat',
                    'option_b': 'Adenin trifosfat',
                    'option_c': 'Amino trifosfat',
                    'option_d': 'Arginin trifosfat',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'Mikroskopni kim ixtiro qilgan?',
                    'option_a': 'Galiley',
                    'option_b': 'Nyuton',
                    'option_c': 'Leeuwenhoek',
                    'option_d': 'Hooke',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'Inson genomida nechta xromosome bor?',
                    'option_a': '44',
                    'option_b': '46',
                    'option_c': '48',
                    'option_d': '50',
                    'correct_answer': 'B'
                }
            ],
            
            'O\'zbek tili': [
                {
                    'question_text': 'O\'zbek tilida nechta unli tovush bor?',
                    'option_a': '5',
                    'option_b': '6',
                    'option_c': '7',
                    'option_d': '8',
                    'correct_answer': 'B'
                },
                {
                    'question_text': '"Chimildiq" so\'zi qaysi so\'z turkumiga kiradi?',
                    'option_a': 'Ot',
                    'option_b': 'Sifat',
                    'option_c': 'Fe\'l',
                    'option_d': 'Ravish',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'Alisher Navoiyning asosiy asari qaysi?',
                    'option_a': 'Xamsa',
                    'option_b': 'Hayrat ul-abror',
                    'option_c': 'Farhod va Shirin',
                    'option_d': 'Layli va Majnun',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'O\'zbek tilida nechta undosh tovush bor?',
                    'option_a': '20',
                    'option_b': '21',
                    'option_c': '22',
                    'option_d': '23',
                    'correct_answer': 'C'
                },
                {
                    'question_text': '"Boburnoma" asarining muallifi kim?',
                    'option_a': 'Alisher Navoiy',
                    'option_b': 'Zahiriddin Muhammad Bobur',
                    'option_c': 'Ahmad Yugnakiy',
                    'option_d': 'Lutfiy',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Qaysi gap turi asosida gap turlari ajratiladi?',
                    'option_a': 'Maqsad',
                    'option_b': 'Tuzilish',
                    'option_c': 'Modal',
                    'option_d': 'Barchasi to\'g\'ri',
                    'correct_answer': 'D'
                },
                {
                    'question_text': '"Yodim keldi allalar yurgan nav mavsum" misrasining muallifi kim?',
                    'option_a': 'Navoiy',
                    'option_b': 'Fuzuliy',
                    'option_c': 'Muqimiy',
                    'option_d': 'Furqat',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'O\'zbek tilida eng kichik ma\'no birligi nima?',
                    'option_a': 'Harf',
                    'option_b': 'Tovush',
                    'option_c': 'Morfema',
                    'option_d': 'So\'z',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'O\'zbek tilining birinchi ilmiy grammatikasi kim tomonidan yozilgan?',
                    'option_a': 'A. Fitrat',
                    'option_b': 'E. Polivanov',
                    'option_c': 'A. Kononov',
                    'option_d': 'N. Baskakov',
                    'correct_answer': 'B'
                },
                {
                    'question_text': '"Muhabbat" so\'zining sinonimi qaysi?',
                    'option_a': 'Ishq',
                    'option_b': 'Nafrat',
                    'option_c': 'Xurram',
                    'option_d': 'Dilrabo',
                    'correct_answer': 'A'
                }
            ],
            
            'Ingliz tili': [
                {
                    'question_text': 'What is the past tense of "go"?',
                    'option_a': 'goed',
                    'option_b': 'went',
                    'option_c': 'gone',
                    'option_d': 'going',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Which article is used before words starting with vowel sounds?',
                    'option_a': 'a',
                    'option_b': 'an',
                    'option_c': 'the',
                    'option_d': 'no article',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Choose the correct form: "I have been ___ English for 5 years."',
                    'option_a': 'study',
                    'option_b': 'studied',
                    'option_c': 'studying',
                    'option_d': 'studies',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'What is the plural of "child"?',
                    'option_a': 'childs',
                    'option_b': 'childes',
                    'option_c': 'children',
                    'option_d': 'child',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'Which sentence is correct?',
                    'option_a': 'She don\'t like coffee',
                    'option_b': 'She doesn\'t like coffee',
                    'option_c': 'She isn\'t like coffee',
                    'option_d': 'She not like coffee',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'What does "bibliography" mean?',
                    'option_a': 'A list of books',
                    'option_b': 'A short story',
                    'option_c': 'A type of library',
                    'option_d': 'An author\'s life story',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'Choose the correct preposition: "I\'m interested ___ learning Spanish."',
                    'option_a': 'in',
                    'option_b': 'on',
                    'option_c': 'at',
                    'option_d': 'for',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'What is the superlative form of "good"?',
                    'option_a': 'gooder',
                    'option_b': 'goodest',
                    'option_c': 'better',
                    'option_d': 'best',
                    'correct_answer': 'D'
                },
                {
                    'question_text': 'Which tense is used for future plans: "I ___ visit London next month."',
                    'option_a': 'will',
                    'option_b': 'am going to',
                    'option_c': 'would',
                    'option_d': 'had',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'What is the correct question form of "She speaks French"?',
                    'option_a': 'Speaks she French?',
                    'option_b': 'Does she speak French?',
                    'option_c': 'Does she speaks French?',
                    'option_d': 'She speaks French?',
                    'correct_answer': 'B'
                }
            ],
            
            'Iqtisodiyot nazariyasi': [
                {
                    'question_text': 'Talab qonuni nimani ifodalaydi?',
                    'option_a': 'Narx oshsa, talab kamayadi',
                    'option_b': 'Narx oshsa, talab oshadi',
                    'option_c': 'Narx o\'zgarmasa, talab o\'zgaradi',
                    'option_d': 'Talab narxga bog\'liq emas',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'Makroiqtisodiyot nimani o\'rganadi?',
                    'option_a': 'Alohida korxonalar',
                    'option_b': 'Iste\'molchi xatti-harakatlari',
                    'option_c': 'Butun iqtisodiyot',
                    'option_d': 'Faqat bozor',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'YaIM nimaning qisqartmasi?',
                    'option_a': 'Yalpi ichki mahsulot',
                    'option_b': 'Yillik ichki mahsulot',
                    'option_c': 'Yelka ichki mahsulot',
                    'option_d': 'Yakka ichki mahsulot',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'Inflyatsiya nima?',
                    'option_a': 'Narxlarning umumiy pasayishi',
                    'option_b': 'Narxlarning umumiy o\'sishi',
                    'option_c': 'Pul miqdorining oshishi',
                    'option_d': 'Ishsizlikning oshishi',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Elastiklik koeffitsienti nimani ko\'rsatadi?',
                    'option_a': 'Narx o\'zgarishi',
                    'option_b': 'Talab sezgirligini',
                    'option_c': 'Foyda miqdorini',
                    'option_d': 'Xarajat hajmini',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Monopoliya nimani anglatadi?',
                    'option_a': 'Ko\'p sotuvchi',
                    'option_b': 'Bitta sotuvchi',
                    'option_c': 'Ko\'p xaridor',
                    'option_d': 'Bitta xaridor',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Daromad elastikligi nima?',
                    'option_a': 'Narx o\'zgarishiga talab reaksiyasi',
                    'option_b': 'Daromad o\'zgarishiga talab reaksiyasi',
                    'option_c': 'Reklama ta\'sirida talab o\'zgarishi',
                    'option_d': 'Mavsum ta\'sirida talab o\'zgarishi',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Perfect raqobat bozorida kimlar qatnashadi?',
                    'option_a': 'Faqat yirik kompaniyalar',
                    'option_b': 'Ko\'p kichik sotuvchi va xaridor',
                    'option_c': 'Bitta sotuvchi va ko\'p xaridor',
                    'option_d': 'Ko\'p sotuvchi va bitta xaridor',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Marjinal xarajat nima?',
                    'option_a': 'Umumiy xarajat',
                    'option_b': 'O\'rtacha xarajat',
                    'option_c': 'Qo\'shimcha bir birlik ishlab chiqarish xarajati',
                    'option_d': 'Doimiy xarajat',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'Iqtisodiy tsiklning bosqichlari qaysilar?',
                    'option_a': 'Faqat o\'sish va pasayish',
                    'option_b': 'O\'sish, cho\'qqi, pasayish, tub',
                    'option_c': 'Faqat cho\'qqi va tub',
                    'option_d': 'O\'sish va cho\'qqi',
                    'correct_answer': 'B'
                }
            ],
            
            'Pedagogika': [
                {
                    'question_text': 'Pedagogikaning asosiy kategoriyalari qaysilar?',
                    'option_a': 'Ta\'lim, tarbiya, rivojlantirish',
                    'option_b': 'Faqat ta\'lim',
                    'option_c': 'Faqat tarbiya',
                    'option_d': 'Faqat rivojlantirish',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'Ya.A.Komenskiy qaysi asarining muallifi?',
                    'option_a': '"Buyuk didaktika"',
                    'option_b': '"Emil"',
                    'option_c': '"Demokratiya va ta\'lim"',
                    'option_d': '"Maktab va jamiyat"',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'Didaktika nima bilan shug\'ullanadi?',
                    'option_a': 'Tarbiya nazariyasi',
                    'option_b': 'O\'qitish nazariyasi',
                    'option_c': 'Boshqarish nazariyasi',
                    'option_d': 'Psixologiya nazariyasi',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Ta\'limning qaysi printsipi asosiy hisoblanadi?',
                    'option_a': 'Ilmiylik printsipi',
                    'option_b': 'Osondan qiyinga',
                    'option_c': 'Mavzulik printsipi',
                    'option_d': 'Hammasi to\'g\'ri',
                    'correct_answer': 'D'
                },
                {
                    'question_text': 'Tarbiyaning qaysi usuli eng samarali?',
                    'option_a': 'Shaxsiy namuna',
                    'option_b': 'Jazo',
                    'option_c': 'Mukofot',
                    'option_d': 'Targ\'ib',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'O\'qitishning qaysi shakli eng keng tarqalgan?',
                    'option_a': 'Individual',
                    'option_b': 'Gruppaviy',
                    'option_c': 'Sinf-dars',
                    'option_d': 'Kurs',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'Pedagogik jarayonning asosiy komponentlari qaysilar?',
                    'option_a': 'Maqsad, mazmun, usul, shakl, vosita',
                    'option_b': 'Faqat maqsad va mazmun',
                    'option_c': 'Faqat usul va shakl',
                    'option_d': 'Faqat o\'qituvchi va o\'quvchi',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'Innovatsion ta\'lim nima?',
                    'option_a': 'Yangi texnologiyalar',
                    'option_b': 'Yangi o\'qitish usullari',
                    'option_c': 'Ta\'limni tubdan yangilash',
                    'option_d': 'Kompyuter ishlatish',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'O\'quvchilarning individual xususiyatlarini hisobga olish qaysi prinsip?',
                    'option_a': 'Individuallashtirish',
                    'option_b': 'Differensiallashtirish',
                    'option_c': 'Munosabatchilik',
                    'option_d': 'Barchasi to\'g\'ri',
                    'correct_answer': 'D'
                },
                {
                    'question_text': 'Maktabda axloqiy tarbiya qaysi fanlar orqali amalga oshiriladi?',
                    'option_a': 'Faqat adabiyot',
                    'option_b': 'Faqat tarix',
                    'option_c': 'Barcha fanlar',
                    'option_d': 'Faqat ma\'naviyat',
                    'correct_answer': 'C'
                }
            ],
            
            'Psixologiya': [
                {
                    'question_text': 'Psixologiyaning predmeti nima?',
                    'option_a': 'Ruhiyat',
                    'option_b': 'Xatti-harakat',
                    'option_c': 'Ong',
                    'option_d': 'Barchasi to\'g\'ri',
                    'correct_answer': 'D'
                },
                {
                    'question_text': 'Z.Freydning psixoanaliz nazariyasida nechta tuzilma bor?',
                    'option_a': '2',
                    'option_b': '3',
                    'option_c': '4',
                    'option_d': '5',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Temperamentning qaysi turi eng faol?',
                    'option_a': 'Sangvinik',
                    'option_b': 'Xolerik',
                    'option_c': 'Melanxolik',
                    'option_d': 'Flegmatik',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Xotiraning qaysi turi eng uzun muddatli?',
                    'option_a': 'Sensorli',
                    'option_b': 'Qisqa muddatli',
                    'option_c': 'Uzoq muddatli',
                    'option_d': 'Operativ',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'Intellekt koeffitsienti qanday belgilanadi?',
                    'option_a': 'EQ',
                    'option_b': 'IQ',
                    'option_c': 'AQ',
                    'option_d': 'PQ',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Stress jarayonini kim o\'rgangan?',
                    'option_a': 'Freyd',
                    'option_b': 'Pavlov',
                    'option_c': 'Selye',
                    'option_d': 'Jung',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'Motivatsiya nima?',
                    'option_a': 'Harakatga undash',
                    'option_b': 'Fikrlash jarayoni',
                    'option_c': 'Hissiy holat',
                    'option_d': 'Xotira jarayoni',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'Bolalar psixologiyasining negizini kim yaratgan?',
                    'option_a': 'Piaget',
                    'option_b': 'Vigotskiy',
                    'option_c': 'Freyberg',
                    'option_d': 'Hall',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'Emosiya va his o\'rtasidagi farq nimada?',
                    'option_a': 'Davomiylikda',
                    'option_b': 'Intensivlikda',
                    'option_c': 'Barqarorlikda',
                    'option_d': 'Barchasi to\'g\'ri',
                    'correct_answer': 'D'
                },
                {
                    'question_text': 'Ijodkorlik qobiliyatini kim o\'rgangan?',
                    'option_a': 'Torrens',
                    'option_b': 'Gilford',
                    'option_c': 'Sternberg',
                    'option_d': 'Barchasi',
                    'correct_answer': 'D'
                }
            ],
            
            # Umumiy savollar (agar fan topilmasa)
            'Umumiy': [
                {
                    'question_text': 'O\'zbekiston Respublikasining poytaxti qaysi shahar?',
                    'option_a': 'Samarqand',
                    'option_b': 'Toshkent',
                    'option_c': 'Buxoro',
                    'option_d': 'Andijon',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Dunyoning eng uzun daryosi qaysi?',
                    'option_a': 'Amazon',
                    'option_b': 'Nil',
                    'option_c': 'Missisipi',
                    'option_d': 'Yangtze',
                    'correct_answer': 'B'
                },
                {
                    'question_text': '2025 yil qaysi asrga tegishli?',
                    'option_a': '20-asr',
                    'option_b': '21-asr',
                    'option_c': '22-asr',
                    'option_d': '19-asr',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Internet qaysi yilda yaratilgan?',
                    'option_a': '1969',
                    'option_b': '1979',
                    'option_c': '1989',
                    'option_d': '1999',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'Alisher Navoiy qaysi asrda yashagan?',
                    'option_a': '14-asr',
                    'option_b': '15-asr',
                    'option_c': '16-asr',
                    'option_d': '17-asr',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Dunyodagi eng baland tog\' qaysi?',
                    'option_a': 'Everest',
                    'option_b': 'K2',
                    'option_c': 'Kilimanjaro',
                    'option_d': 'Elbrus',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'BMT necha yilda tashkil etilgan?',
                    'option_a': '1944',
                    'option_b': '1945',
                    'option_c': '1946',
                    'option_d': '1947',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Quyoshdan Yerga yorug\'lik necha daqiqada yetib keladi?',
                    'option_a': '6 daqiqa',
                    'option_b': '8 daqiqa',
                    'option_c': '10 daqiqa',
                    'option_d': '12 daqiqa',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Kompyuterning asosiy xotirasi qanday nomlanadi?',
                    'option_a': 'CPU',
                    'option_b': 'RAM',
                    'option_c': 'ROM',
                    'option_d': 'GPU',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'O\'zbekistonda nechta viloyat bor?',
                    'option_a': '12',
                    'option_b': '13',
                    'option_c': '14',
                    'option_d': '15',
                    'correct_answer': 'C'
                }
            ]
        }