from django.contrib import admin
from .models import Branch, EducationLevel, EducationForm, Program


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(EducationLevel)
class EducationLevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(EducationForm)
class EducationFormAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'code',
        'branch',
        'education_level',
        'education_form',
        'tuition_fee',
        'study_duration',
        'contract_series'
    )
    list_filter = ('branch', 'education_level', 'education_form')
    search_fields = ('name', 'code', 'contract_series')
    readonly_fields = ('image_preview',)
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'branch', 'education_level', 'education_form')
        }),
        ('Qo‘shimcha maʼlumotlar', {
            'fields': ('tuition_fee', 'study_duration', 'contract_series', 'image', 'image_preview')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="150" />'
        return "Rasm mavjud emas"
    image_preview.short_description = "Rasm ko‘rinishi"
    image_preview.allow_tags = True
