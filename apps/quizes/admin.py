from django.contrib import admin
from django.utils.html import format_html
from .models import Subject, ProgramTest, Question, TestAttempt, Answer, TestResult


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']
    ordering = ['name']


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = [
        'subject_type', 'question_number', 'question_text', 
        'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer'
    ]
    ordering = ['subject_type', 'question_number']


@admin.register(ProgramTest)
class ProgramTestAdmin(admin.ModelAdmin):
    list_display = [
        'program', 'get_subjects', 'passing_score', 'time_limit',
        'questions_status', 'is_active'
    ]
    list_filter = ['subject_1', 'subject_2', 'is_active']
    search_fields = ['program__name', 'subject_1__name', 'subject_2__name']
    inlines = [QuestionInline]
    
    fieldsets = (
        ('Yo\'nalish va fanlar', {
            'fields': ('program', 'subject_1', 'subject_2')
        }),
        ('Sozlamalar', {
            'fields': ('passing_score', 'time_limit', 'is_active')
        }),
    )
    
    def get_subjects(self, obj):
        return f"{obj.subject_1.name} + {obj.subject_2.name}"
    get_subjects.short_description = 'Fanlar'
    
    def questions_status(self, obj):
        total_questions = obj.questions.count()
        subject_1_count = obj.questions.filter(subject_type='subject_1').count()
        subject_2_count = obj.questions.filter(subject_type='subject_2').count()
        
        if subject_1_count == 10 and subject_2_count == 10:
            return format_html('<span style="color: green;">✅ 20/20 (10+10)</span>')
        else:
            return format_html('<span style="color: red;">❌ {}/20 ({}+{})</span>', 
                             total_questions, subject_1_count, subject_2_count)
    questions_status.short_description = 'Savollar'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = [
        'program_test', 'get_subject_name', 'question_number', 
        'get_question_preview', 'correct_answer'
    ]
    list_filter = ['program_test', 'subject_type', 'correct_answer']
    search_fields = ['question_text', 'program_test__program__name']
    ordering = ['program_test', 'subject_type', 'question_number']
    
    fieldsets = (
        ('Asosiy', {
            'fields': ('program_test', 'subject_type', 'question_number', 'question_text')
        }),
        ('Javoblar', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'correct_answer')
        }),
    )
    
    def get_subject_name(self, obj):
        return obj.get_subject_name()
    get_subject_name.short_description = 'Fan'
    
    def get_question_preview(self, obj):
        return obj.question_text[:50] + "..." if len(obj.question_text) > 50 else obj.question_text
    get_question_preview.short_description = 'Savol'


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ['question', 'selected_answer', 'is_correct', 'answered_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = [
        'get_user_name', 'get_program', 'attempt_number', 'status',
        'total_score', 'percentage', 'is_passed', 'get_subject_scores', 'started_at'
    ]
    list_filter = [
        'status', 'is_passed', 'program_test__program', 'started_at'
    ]
    search_fields = [
        'application__user__phone', 'application__user__full_name',
        'program_test__program__name'
    ]
    readonly_fields = [
        'application', 'program_test', 'started_at', 'completed_at',
        'total_score', 'percentage', 'is_passed'
    ]
    inlines = [AnswerInline]
    
    fieldsets = (
        ('Asosiy', {
            'fields': ('application', 'program_test', 'attempt_number', 'status')
        }),
        ('Vaqt', {
            'fields': ('started_at', 'completed_at', 'time_spent')
        }),
        ('Natijalar', {
            'fields': (
                'subject_1_score', 'subject_2_score', 'total_score', 
                'percentage', 'is_passed'
            )
        }),
    )
    
    def get_user_name(self, obj):
        return obj.application.user.full_name or obj.application.user.phone
    get_user_name.short_description = 'Foydalanuvchi'
    
    def get_program(self, obj):
        return obj.program_test.program.name
    get_program.short_description = 'Yo\'nalish'
    
    def get_subject_scores(self, obj):
        return f"{obj.subject_1_score} + {obj.subject_2_score}"
    get_subject_scores.short_description = 'Fan ballari'
    
    actions = ['recalculate_results']
    
    def recalculate_results(self, request, queryset):
        for attempt in queryset:
            attempt.calculate_results()
        self.message_user(request, f"{queryset.count()} ta natija qayta hisoblandi.")
    recalculate_results.short_description = "Natijalarni qayta hisoblash"


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = [
        'get_user_name', 'get_program', 'best_total_score', 'best_percentage',
        'is_test_passed', 'total_attempts', 'last_attempt_date'
    ]
    list_filter = ['is_test_passed', 'application__program', 'last_attempt_date']
    search_fields = [
        'application__user__phone', 'application__user__full_name',
        'application__program__name'
    ]
    readonly_fields = [
        'application', 'best_attempt', 'best_total_score', 'best_percentage',
        'is_test_passed', 'best_subject_1_score', 'best_subject_2_score',
        'total_attempts', 'last_attempt_date'
    ]
    
    fieldsets = (
        ('Asosiy', {
            'fields': ('application', 'best_attempt')
        }),
        ('Eng yaxshi natija', {
            'fields': (
                'best_total_score', 'best_percentage', 'is_test_passed',
                'best_subject_1_score', 'best_subject_2_score'
            )
        }),
        ('Statistika', {
            'fields': ('total_attempts', 'last_attempt_date')
        }),
    )
    
    def get_user_name(self, obj):
        return obj.application.user.full_name or obj.application.user.phone
    get_user_name.short_description = 'Foydalanuvchi'
    
    def get_program(self, obj):
        return obj.application.program.name
    get_program.short_description = 'Yo\'nalish'
    
    actions = ['update_best_results']
    
    def update_best_results(self, request, queryset):
        for result in queryset:
            result.update_best_result()
        self.message_user(request, f"{queryset.count()} ta natija yangilandi.")
    update_best_results.short_description = "Eng yaxshi natijalarni yangilash"