# Generated by Django 5.2.1 on 2025-06-03 14:19

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('regions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('phone', models.CharField(help_text='Masalan: +998901234567', max_length=13, unique=True, validators=[django.core.validators.RegexValidator(message="Telefon raqam +998XXXXXXXXX formatida bo'lishi kerak", regex='^\\+998\\d{9}$')], verbose_name='Telefon raqami')),
                ('full_name', models.CharField(blank=True, help_text="Foydalanuvchining to'liq ismi", max_length=255, null=True, verbose_name="To'liq ismi")),
                ('is_verified', models.BooleanField(default=False, help_text='Telefon raqami SMS kod orqali tasdiqlangan', verbose_name='SMS kod orqali tasdiqlanganmi?')),
                ('role', models.CharField(choices=[('abituriyent', 'Abituriyent'), ('operator', 'Operator'), ('marketing', 'Marketing'), ('mini_admin', 'Mini Admin'), ('admin', 'Admin')], default='abituriyent', help_text='Tizimda foydalanuvchi roli', max_length=20, verbose_name='Foydalanuvchi roli')),
                ('is_active', models.BooleanField(default=True, help_text='Foydalanuvchi faol holatda', verbose_name='Faol holat')),
                ('is_staff', models.BooleanField(default=False, help_text='Admin panelga kirish huquqi', verbose_name='Xodim')),
                ('date_joined', models.DateTimeField(auto_now_add=True, help_text="Foydalanuvchi ro'yxatdan o'tgan vaqt", verbose_name="Ro'yxatdan o'tgan vaqti")),
                ('last_login_attempt', models.DateTimeField(blank=True, help_text='Oxirgi marta tizimga kirish urinishi', null=True, verbose_name='Oxirgi kirish urinishi')),
                ('failed_login_attempts', models.PositiveIntegerField(default=0, help_text='Ketma-ket muvaffaqiyatsiz kirish urinishlari soni', verbose_name='Muvaffaqiyatsiz kirish urinishlari')),
                ('is_blocked', models.BooleanField(default=False, help_text='Foydalanuvchi vaqtincha bloklangan', verbose_name='Bloklangan')),
                ('blocked_until', models.DateTimeField(blank=True, help_text='Blok tugash vaqti', null=True, verbose_name='Blok tugash vaqti')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Foydalanuvchi',
                'verbose_name_plural': 'Foydalanuvchilar',
                'ordering': ['-date_joined'],
            },
        ),
        migrations.CreateModel(
            name='AbituriyentProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Profil yaratilgan vaqt', verbose_name='Yaratilgan vaqti')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Profil oxirgi yangilangan vaqt', verbose_name='Yangilangan vaqti')),
                ('last_name', models.CharField(help_text='Abituriyent familiyasi', max_length=100, verbose_name='Familiya')),
                ('first_name', models.CharField(help_text='Abituriyent ismi', max_length=100, verbose_name='Ism')),
                ('other_name', models.CharField(help_text='Abituriyent otasining ismi', max_length=100, verbose_name='Otasining ismi')),
                ('birth_date', models.DateField(help_text="Abituriyent tug'ilgan sanasi", verbose_name="Tug'ilgan sana")),
                ('passport_series', models.CharField(help_text='Masalan: AA1234567', max_length=9, unique=True, validators=[django.core.validators.RegexValidator(message="Pasport seriyasi XX1234567 formatida bo'lishi kerak", regex='^[A-Z]{2}\\d{7}$')], verbose_name='Pasport seriyasi va raqami')),
                ('pinfl', models.CharField(help_text='14 raqamdan iborat PINFL kodi', max_length=14, unique=True, validators=[django.core.validators.RegexValidator(message="PINFL 14 ta raqamdan iborat bo'lishi kerak", regex='^\\d{14}$')], verbose_name='JShShIR (PINFL)')),
                ('address', models.TextField(blank=True, help_text="To'liq yashash manzili", null=True, verbose_name='Yashash manzili')),
                ('gender', models.CharField(choices=[('erkak', 'Erkak'), ('ayol', 'Ayol')], help_text='Abituriyent jinsi', max_length=10, verbose_name='Jinsi')),
                ('nationality', models.CharField(default="O'zbek", help_text='Abituriyent millati', max_length=50, verbose_name='Millati')),
                ('image', models.ImageField(help_text="3x4 o'lchamdagi rasm (JPG, PNG)", upload_to='users/abituriyents/images/%Y/%m/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])], verbose_name='3x4 rasm')),
                ('passport_file', models.FileField(help_text='Pasport nusxasi (PDF, JPG, PNG)', upload_to='users/abituriyents/passports/%Y/%m/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])], verbose_name='Pasport nusxasi')),
                ('district', models.ForeignKey(blank=True, help_text='Abituriyent yashash tumani', null=True, on_delete=django.db.models.deletion.SET_NULL, to='regions.district', verbose_name='Tuman')),
                ('region', models.ForeignKey(blank=True, help_text='Abituriyent yashash viloyati', null=True, on_delete=django.db.models.deletion.SET_NULL, to='regions.region', verbose_name='Viloyat')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='abituriyent_profile', to=settings.AUTH_USER_MODEL, verbose_name='Foydalanuvchi')),
            ],
            options={
                'verbose_name': 'Abituriyent profili',
                'verbose_name_plural': 'Abituriyentlar profillari',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AdminProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Profil yaratilgan vaqt', verbose_name='Yaratilgan vaqti')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Profil oxirgi yangilangan vaqt', verbose_name='Yangilangan vaqti')),
                ('access_level', models.CharField(choices=[('super', 'Super Admin'), ('system', 'Tizim Admin'), ('regional', 'Hududiy Admin')], default='regional', help_text='Admin kirish huquqlari darajasi', max_length=20, verbose_name='Kirish darajasi')),
                ('can_modify_users', models.BooleanField(default=True, help_text="Boshqa foydalanuvchilarni o'zgartirish huquqi", verbose_name="Foydalanuvchilarni o'zgartirish huquqi")),
                ('can_access_reports', models.BooleanField(default=True, help_text='Tizim hisobotlariga kirish huquqi', verbose_name='Hisobotlarga kirish huquqi')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='admin_profile', to=settings.AUTH_USER_MODEL, verbose_name='Foydalanuvchi')),
            ],
            options={
                'verbose_name': 'Admin profili',
                'verbose_name_plural': 'Adminlar profillari',
            },
        ),
        migrations.CreateModel(
            name='MarketingProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Profil yaratilgan vaqt', verbose_name='Yaratilgan vaqti')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Profil oxirgi yangilangan vaqt', verbose_name='Yangilangan vaqti')),
                ('department', models.CharField(blank=True, help_text="Shartnoma bo'limi", max_length=100, null=True, verbose_name="Bo'lim")),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='marketing_profile', to=settings.AUTH_USER_MODEL, verbose_name='Foydalanuvchi')),
            ],
            options={
                'verbose_name': 'Marketing xodimi profili',
                'verbose_name_plural': 'Marketing xodimlari profillari',
            },
        ),
        migrations.CreateModel(
            name='MiniAdminProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Profil yaratilgan vaqt', verbose_name='Yaratilgan vaqti')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Profil oxirgi yangilangan vaqt', verbose_name='Yangilangan vaqti')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='mini_admin_profile', to=settings.AUTH_USER_MODEL, verbose_name='Foydalanuvchi')),
            ],
            options={
                'verbose_name': 'Mini Admin profili',
                'verbose_name_plural': 'Mini Adminlar profillari',
            },
        ),
        migrations.CreateModel(
            name='OperatorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Profil yaratilgan vaqt', verbose_name='Yaratilgan vaqti')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Profil oxirgi yangilangan vaqt', verbose_name='Yangilangan vaqti')),
                ('shift', models.CharField(blank=True, help_text='Operator ish smenasi', max_length=50, null=True, verbose_name='Ish smenasi')),
                ('handled_applications', models.PositiveIntegerField(default=0, help_text="Operator tomonidan ko'rib chiqilgan arizalar soni", verbose_name="Ko'rib chiqilgan arizalar soni")),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='operator_profile', to=settings.AUTH_USER_MODEL, verbose_name='Foydalanuvchi')),
            ],
            options={
                'verbose_name': 'Operator profili',
                'verbose_name_plural': 'Operatorlar profillari',
            },
        ),
        migrations.CreateModel(
            name='PhoneVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(help_text='Tasdiqlash kodi yuborilgan telefon raqami', max_length=13, validators=[django.core.validators.RegexValidator(message="Telefon raqam +998XXXXXXXXX formatida bo'lishi kerak", regex='^\\+998\\d{9}$')], verbose_name='Telefon raqami')),
                ('code', models.CharField(help_text='4 raqamli tasdiqlash kodi', max_length=4, validators=[django.core.validators.RegexValidator(message="Tasdiqlash kodi 4 ta raqamdan iborat bo'lishi kerak", regex='^\\d{6}$')], verbose_name='Tasdiqlash kodi')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Tasdiqlash kodi yaratilgan vaqt', verbose_name='Yaratilgan vaqti')),
                ('is_used', models.BooleanField(default=False, help_text='Tasdiqlash kodi ishlatilgan', verbose_name='Ishlatilgan')),
                ('attempts', models.PositiveIntegerField(default=0, help_text="Noto'g'ri kiritish urinishlari soni", verbose_name='Urinishlar soni')),
            ],
            options={
                'verbose_name': 'Telefon tasdiqlash',
                'verbose_name_plural': 'Telefon tasdiqlash kodlari',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['phone', 'created_at'], name='users_phone_phone_6280bb_idx'), models.Index(fields=['code', 'is_used'], name='users_phone_code_17f453_idx')],
            },
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['phone'], name='users_user_phone_9474e8_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['role'], name='users_user_role_36d76d_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['is_active'], name='users_user_is_acti_ddda02_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['date_joined'], name='users_user_date_jo_064c8f_idx'),
        ),
        migrations.AddIndex(
            model_name='abituriyentprofile',
            index=models.Index(fields=['passport_series'], name='users_abitu_passpor_72c68e_idx'),
        ),
        migrations.AddIndex(
            model_name='abituriyentprofile',
            index=models.Index(fields=['pinfl'], name='users_abitu_pinfl_1edd90_idx'),
        ),
        migrations.AddIndex(
            model_name='abituriyentprofile',
            index=models.Index(fields=['region', 'district'], name='users_abitu_region__10d824_idx'),
        ),
    ]
