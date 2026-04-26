from django.contrib import admin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'status', 'created_at')
    list_filter = ('role', 'status')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-created_at',)


from .models import Classe, Groupe


@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ('nom', 'created_at')
    list_filter = ('nom',)


@admin.register(Groupe)
class GroupeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'classe', 'created_at')
    list_filter = ('classe',)
    search_fields = ('nom',)
