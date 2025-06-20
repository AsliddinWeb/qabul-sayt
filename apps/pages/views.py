from django.shortcuts import render
from apps.programs.models import Branch, EducationLevel, EducationForm, Program
from collections import defaultdict


def home_page(request):
    # Barcha asosiy ma'lumotlarni olish
    branches = Branch.objects.all()
    education_levels = EducationLevel.objects.all()
    education_forms = EducationForm.objects.all()

    # Barcha yo'nalishlarni olish
    all_programs = Program.objects.all()

    # Bir xil nomli yo'nalishlarni birlashtirib, education_form larni to'plash
    grouped_programs = defaultdict(lambda: {
        'program': None,
        'education_forms': [],
        'branches': set(),
        'tuition_fees': set(),
        'study_durations': set(),
    })

    for program in all_programs:
        key = (program.name, program.education_level.id)

        if grouped_programs[key]['program'] is None:
            grouped_programs[key]['program'] = program

        grouped_programs[key]['education_forms'].append(program.education_form.name)
        grouped_programs[key]['branches'].add(program.branch.name)
        grouped_programs[key]['tuition_fees'].add(program.tuition_fee)
        grouped_programs[key]['study_durations'].add(program.study_duration)

    # Guruhlanrgan dasturlarni featured_programs formatiga o'tkazish
    featured_programs = []
    for key, data in grouped_programs.items():
        program = data['program']
        # Yangi obyekt yaratish (original obyektni o'zgartimaslik uchun)
        program_copy = type('Program', (), {})()
        program_copy.id = program.id
        program_copy.name = program.name
        program_copy.education_level = program.education_level
        program_copy.branch = program.branch
        program_copy.tuition_fee = program.tuition_fee
        program_copy.study_duration = program.study_duration

        # Education formlarni vergul bilan birlashtirish
        program_copy.education_form_names = ', '.join(set(data['education_forms']))
        program_copy.education_form = program.education_form  # Original education_form ham kerak bo'lishi mumkin

        # Agar bir nechta branch, fee, duration bo'lsa, ularni ham ko'rsatish mumkin
        program_copy.all_branches = ', '.join(data['branches'])
        program_copy.all_tuition_fees = ', '.join(map(str, data['tuition_fees']))
        program_copy.all_study_durations = ', '.join(data['study_durations'])

        featured_programs.append(program_copy)

    # Ta'lim darajasi bo'yicha yo'nalishlar
    # bakalavr_programs = Program.objects.filter(education_level__name__icontains='bakalavr')[:3]
    # magistr_programs = Program.objects.filter(education_level__name__icontains='magistr')[:3]
    # doktorantura_programs = Program.objects.filter(education_level__name__icontains='doktor')[:3]

    # Statistika uchun
    total_programs = Program.objects.count()
    total_branches = branches.count()
    total_students = 5000  # Bu qiymatni database dan olish mumkin
    employment_rate = 95  # Bu qiymatni database dan olish mumkin

    ctx = {
        'branches': branches,
        'education_levels': education_levels,
        'education_forms': education_forms,
        'featured_programs': featured_programs,
        # 'bakalavr_programs': bakalavr_programs,
        # 'magistr_programs': magistr_programs,
        # 'doktorantura_programs': doktorantura_programs,
        'total_programs': total_programs,
        'total_branches': total_branches,
        'total_students': total_students,
        'employment_rate': employment_rate,
    }
    return render(request, 'home/home.html', ctx)