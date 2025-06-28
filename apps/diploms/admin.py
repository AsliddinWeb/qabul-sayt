from django.contrib import admin
from .models import (
    EducationType,
    InstitutionType,
    Course,
    Diplom,
    TransferDiplom,
)


@admin.register(EducationType)
class EducationTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('-id',)


@admin.register(InstitutionType)
class InstitutionTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('-id',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('-id',)


@admin.register(Diplom)
class DiplomAdmin(admin.ModelAdmin):
    list_display = ('id', 'serial_number', 'user', 'education_type', 'institution_type', 'graduation_year')
    search_fields = ('serial_number', 'user__phone', 'university_name')
    list_filter = ('education_type', 'institution_type', 'region', 'district')
    ordering = ('-id',)
    readonly_fields = ('serial_number',)  # Foydalanuvchiga faqat ko‘rsatish uchun, agar kerak bo‘lsa
    fieldsets = (
        (None, {
            'fields': ('user', 'serial_number', 'education_type', 'institution_type', 'university_name', 'graduation_year')
        }),
        ("Manzil", {
            'fields': ('region', 'district')
        }),
        ("Fayl", {
            'fields': ('diploma_file',)
        }),
    )


@admin.register(TransferDiplom)
class TransferDiplomAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'country', 'university_name', 'target_course')
    search_fields = ('user__phone', 'university_name', 'country__name')
    list_filter = ('country', 'target_course')
    ordering = ('user__phone',)
    fieldsets = (
        (None, {
            'fields': ('user', 'country', 'university_name', 'target_course', 'transcript_file')
        }),
    )
