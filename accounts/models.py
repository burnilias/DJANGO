from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('status', 'active')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('desactive', 'Désactivé'),
        ('veille', 'En veille'),
    ]

    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # hashed via set_password / make_password
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    phone = models.CharField(max_length=30, blank=True, default='')
    bio = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    groupe = models.ForeignKey('Groupe', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)  # Django internal flag

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f'{self.email} ({self.role})'

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    @property
    def is_status_active(self):
        return self.status == 'active'


class Schedule(models.Model):
    SCHEDULE_TYPES = [
        ('cours', 'Cours'),
        ('controle', 'Contrôle'),
        ('examen', 'Examen'),
        ('rattrapage', 'Rattrapage'),
    ]
    
    DAYS = [
        ('1', 'Lundi'),
        ('2', 'Mardi'),
        ('3', 'Mercredi'),
        ('4', 'Jeudi'),
        ('5', 'Vendredi'),
        ('6', 'Samedi'),
        ('7', 'Dimanche'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    room = models.CharField(max_length=50, blank=True, default='')
    day_of_week = models.CharField(max_length=1, choices=DAYS, default='1')
    start_time = models.TimeField()
    end_time = models.TimeField()
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPES, default='cours')
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'}, null=True, blank=True)
    groupe = models.ForeignKey('Groupe', on_delete=models.SET_NULL, null=True, blank=True, related_name='schedules')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'emplois_du_temps'
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.name} ({self.get_day_of_week_display()} {self.start_time.strftime('%H:%M')})"
    
    @property
    def color_class(self):
        colors = {
            'cours': 'bg-blue-200 border-blue-400 text-blue-900',
            'controle': 'bg-yellow-200 border-yellow-400 text-yellow-900',
            'examen': 'bg-green-200 border-green-400 text-green-900',
            'rattrapage': 'bg-red-200 border-red-400 text-red-900',
        }
        return colors.get(self.schedule_type, 'bg-gray-200 border-gray-400')
    
    @property
    def type_label(self):
        labels = {
            'cours': 'Cours',
            'controle': 'Contrôle',
            'examen': 'Examen',
            'rattrapage': 'Rattrapage',
        }
        return labels.get(self.schedule_type, 'Cours')


class Classe(models.Model):
    NOM_CHOICES = [
        ('1ère Année', '1ère Année'),
        ('2ème Année', '2ème Année'),
        ('3ème Année', '3ème Année'),
        ('4ème Année', '4ème Année'),
        ('5ème Année', '5ème Année'),
    ]
    nom = models.CharField(max_length=20, choices=NOM_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'classes'

    def __str__(self):
        return self.nom


class Groupe(models.Model):
    nom = models.CharField(max_length=50)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='groupes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'groupes'

    def __str__(self):
        return f"{self.nom} - {self.classe.nom}"
