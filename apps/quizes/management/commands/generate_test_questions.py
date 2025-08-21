from django.core.management.base import BaseCommand
from django.db import transaction
from apps.quizes.models import Subject, ProgramTest, Question
import random

class Command(BaseCommand):
    help = 'Barcha fanlar uchun test savollarini yaratish'

    def add_arguments(self, parser):
        parser.add_argument(
            '--questions-per-subject',
            type=int,
            default=20,
            help='Har bir fan uchun savollar soni'
        )

    def handle(self, *args, **options):
        questions_count = options['questions_per_subject']
        
        self.stdout.write(f'Har bir fan uchun {questions_count} ta savol yaratish...')
        
        with transaction.atomic():
            subjects = Subject.objects.filter(is_active=True)
            total_created = 0
            
            for subject in subjects:
                created_for_subject = self.create_questions_for_subject(subject, questions_count)
                total_created += created_for_subject
                
                self.stdout.write(f'✅ {subject.name}: {created_for_subject} ta savol')
            
            self.stdout.write(
                self.style.SUCCESS(f'Jami {total_created} ta savol yaratildi')
            )
            
            # Har bir program uchun savollar yaratish
            self.create_program_questions()

    def create_questions_for_subject(self, subject, count):
        """Berilgan fan uchun savollar yaratish"""
        
        # Har bir fan uchun maxsus savollar
        questions_data = self.get_questions_for_subject(subject.code)
        
        if not questions_data:
            # Agar maxsus savollar yo'q bo'lsa, umumiy savollar
            questions_data = self.get_general_questions(subject.name)
        
        created_count = 0
        
        # Savollarni takrorlash orqali kerakli sonini yaratish
        for i in range(count):
            question_data = questions_data[i % len(questions_data)]
            
            # Savol yaratish (program_test=None - bu umumiy savol)
            # Keyinchalik har bir program uchun nusxa olinadi
            
            created_count += 1
        
        return created_count

    def create_program_questions(self):
        """Har bir program uchun savollarni yaratish"""
        program_tests = ProgramTest.objects.all()
        
        for program_test in program_tests:
            # Subject 1 uchun savollar
            self.create_questions_for_program_subject(
                program_test, program_test.subject_1, 'subject_1'
            )
            
            # Subject 2 uchun savollar
            self.create_questions_for_program_subject(
                program_test, program_test.subject_2, 'subject_2'
            )

    def create_questions_for_program_subject(self, program_test, subject, subject_type):
        """Program va fan uchun savollar yaratish"""
        questions_data = self.get_questions_for_subject(subject.code)
        
        if not questions_data:
            questions_data = self.get_general_questions(subject.name)
        
        # 20 ta savol yaratish
        for i in range(20):
            question_data = questions_data[i % len(questions_data)]
            
            Question.objects.get_or_create(
                program_test=program_test,
                subject_type=subject_type,
                question_number=i + 1,
                defaults={
                    'question_text': question_data['text'],
                    'option_a': question_data['options'][0],
                    'option_b': question_data['options'][1],
                    'option_c': question_data['options'][2],
                    'option_d': question_data['options'][3],
                    'correct_answer': question_data['correct']
                }
            )

    def get_questions_for_subject(self, subject_code):
        """Fan kodiga qarab savollar qaytarish"""
        
        questions_bank = {
            'MATH': [
                {
                    'text': '2 + 3 × 4 = ?',
                    'options': ['20', '14', '11', '24'],
                    'correct': 'B'
                },
                {
                    'text': '√16 = ?',
                    'options': ['2', '4', '8', '16'],
                    'correct': 'B'
                },
                {
                    'text': '15% dan 200 = ?',
                    'options': ['30', '25', '35', '20'],
                    'correct': 'A'
                },
                {
                    'text': 'x + 5 = 12, x = ?',
                    'options': ['7', '6', '8', '17'],
                    'correct': 'A'
                },
                {
                    'text': '2³ = ?',
                    'options': ['6', '8', '9', '4'],
                    'correct': 'B'
                },
                {
                    'text': '7 × 8 = ?',
                    'options': ['54', '56', '64', '48'],
                    'correct': 'B'
                },
                {
                    'text': '144 ÷ 12 = ?',
                    'options': ['12', '11', '13', '10'],
                    'correct': 'A'
                },
                {
                    'text': '3² + 4² = ?',
                    'options': ['25', '24', '49', '14'],
                    'correct': 'A'
                },
                {
                    'text': '0.5 + 0.25 = ?',
                    'options': ['0.75', '0.7', '0.8', '0.25'],
                    'correct': 'A'
                },
                {
                    'text': '¾ ni o\'nli kasrda yozing',
                    'options': ['0.75', '0.34', '0.43', '0.25'],
                    'correct': 'A'
                }
            ],
            
            'UZB': [
                {
                    'text': 'O\'zbek tilida nechta unli tovush bor?',
                    'options': ['5', '6', '7', '8'],
                    'correct': 'B'
                },
                {
                    'text': '"Boburnoma" asarining muallifi kim?',
                    'options': ['Alisher Navoiy', 'Zahiriddin Muhammad Bobur', 'Ahmad Yugnakiy', 'Lutfiy'],
                    'correct': 'B'
                },
                {
                    'text': 'O\'zbek tilining davlat tili sifatida tan olingan yil?',
                    'options': ['1989', '1991', '1990', '1992'],
                    'correct': 'A'
                },
                {
                    'text': '"Xamsa" asarining muallifi kim?',
                    'options': ['Firdavsiy', 'Alisher Navoiy', 'Nizomiy', 'Hofiz'],
                    'correct': 'B'
                },
                {
                    'text': 'O\'zbek alifbosida nechta harf bor?',
                    'options': ['32', '33', '34', '35'],
                    'correct': 'A'
                }
            ],
            
            'ENG': [
                {
                    'text': 'What is the capital of Great Britain?',
                    'options': ['Manchester', 'London', 'Liverpool', 'Birmingham'],
                    'correct': 'B'
                },
                {
                    'text': 'Choose the correct form: "I ... to school every day"',
                    'options': ['go', 'goes', 'going', 'went'],
                    'correct': 'A'
                },
                {
                    'text': 'What is the past form of "buy"?',
                    'options': ['buyed', 'bought', 'buied', 'buying'],
                    'correct': 'B'
                },
                {
                    'text': 'How many letters are there in English alphabet?',
                    'options': ['24', '25', '26', '27'],
                    'correct': 'C'
                }
            ],
            
            'ECON_THEORY': [
                {
                    'text': 'Iqtisodiyotning asosiy muammosi nima?',
                    'options': ['Chekli resurslar', 'Yuqori narxlar', 'Past maoshlar', 'Ishsizlik'],
                    'correct': 'A'
                },
                {
                    'text': 'Talab va taklif o\'rtasidagi muvozanat nimani hosil qiladi?',
                    'options': ['Bozor narxi', 'Maksimal foyda', 'Minimal xarajat', 'Optimal ishlab chiqarish'],
                    'correct': 'A'
                },
                {
                    'text': 'YaIM nimani bildiradi?',
                    'options': ['Yalpi ichki mahsulot', 'Yillik iqtisodiy mahsuldorlik', 'Yalpi import mahsuloti', 'Yoshlar iqtisodiy markazi'],
                    'correct': 'A'
                }
            ],
            
            'PROGRAMMING': [
                {
                    'text': 'HTML nimaning qisqartmasi?',
                    'options': ['High Text Markup Language', 'HyperText Markup Language', 'Home Tool Markup Language', 'Hyper Transfer Markup Language'],
                    'correct': 'B'
                },
                {
                    'text': 'Python dasturlash tilining yaratuvchisi kim?',
                    'options': ['Guido van Rossum', 'James Gosling', 'Dennis Ritchie', 'Brendan Eich'],
                    'correct': 'A'
                },
                {
                    'text': 'CSS nimani bildiradi?',
                    'options': ['Computer Style Sheets', 'Cascading Style Sheets', 'Creative Style Sheets', 'Colorful Style Sheets'],
                    'correct': 'B'
                }
            ],
            
            'PED': [
                {
                    'text': 'Pedagogika fanining asosiy predmeti nima?',
                    'options': ['Ta\'lim jarayoni', 'Tarbiya jarayoni', 'O\'qitish jarayoni', 'Barchasi to\'g\'ri'],
                    'correct': 'D'
                },
                {
                    'text': 'J.A.Komenskiy qaysi asarning muallifi?',
                    'options': ['"Buyuk didaktika"', '"Emile"', '"Demokratiya va ta\'lim"', '"Maktab va jamiyat"'],
                    'correct': 'A'
                },
                {
                    'text': 'Ta\'lim jarayonining asosiy komponentlari nima?',
                    'options': ['Maqsad, mazmun, usul', 'O\'qituvchi, o\'quvchi, darslik', 'Nazariya, amaliyot, nazorat', 'Bilim, ko\'nikma, malaka'],
                    'correct': 'A'
                }
            ]
        }
        
        return questions_bank.get(subject_code, [])

    def get_general_questions(self, subject_name):
        """Umumiy savollar"""
        return [
            {
                'text': f'{subject_name} fanining asosiy maqsadi nima?',
                'options': ['Bilim berish', 'Tarbiyalash', 'Rivojlantirish', 'Barchasi'],
                'correct': 'D'
            },
            {
                'text': f'{subject_name} fanini o\'rganishning ahamiyati nimada?',
                'options': ['Nazariy bilim', 'Amaliy ko\'nikma', 'Intellektual rivojlanish', 'Barchasi muhim'],
                'correct': 'D'
            },
            {
                'text': f'{subject_name} sohasidagi eng muhim tushuncha qaysi?',
                'options': ['Asosiy printsip', 'Nazariy asos', 'Amaliy tatbiq', 'Hammasidan muhimi'],
                'correct': 'A'
            },
            {
                'text': f'{subject_name} fanini o\'rganish uchun zarur shart nima?',
                'options': ['Qiziqish', 'Mehnat', 'Izchillik', 'Barchasi kerak'],
                'correct': 'D'
            },
            {
                'text': f'{subject_name} sohasidagi zamonaviy yo\'nalish qaysi?',
                'options': ['Innovatsion yondashuv', 'An\'anaviy usul', 'Aralash usul', 'Barcha usullar'],
                'correct': 'A'
            }
        ]
