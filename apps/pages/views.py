from django.shortcuts import render
from apps.programs.models import Branch, EducationLevel, EducationForm, Program


def home_page(request):
    # Barcha asosiy ma'lumotlarni olish
    branches = Branch.objects.all()
    education_levels = EducationLevel.objects.all()
    education_forms = EducationForm.objects.all()

    # Mashhur yo'nalishlar (eng ko'p qidirilganlar yoki tavsiya etiladiganlar)
    featured_programs = Program.objects.all()[:6]  # Birinchi 6 tasini olish

    # Ta'lim darajasi bo'yicha yo'nalishlar
    bakalavr_programs = Program.objects.filter(education_level__name__icontains='bakalavr')[:3]
    magistr_programs = Program.objects.filter(education_level__name__icontains='magistr')[:3]
    doktorantura_programs = Program.objects.filter(education_level__name__icontains='doktor')[:3]

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
        'bakalavr_programs': bakalavr_programs,
        'magistr_programs': magistr_programs,
        'doktorantura_programs': doktorantura_programs,
        'total_programs': total_programs,
        'total_branches': total_branches,
        'total_students': total_students,
        'employment_rate': employment_rate,
    }
    return render(request, 'home/home.html', ctx)