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


from .models import CV


@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'updated_at')
    list_filter = ('user__role',)
    search_fields = ('title', 'user__email')
    ordering = ('-updated_at',)


from .models import LessonVideo, VideoCompletion


@admin.register(LessonVideo)
class LessonVideoAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'title', 'url', 'order')
    list_filter = ('lesson__course',)
    search_fields = ('title', 'url')
    ordering = ('order',)


@admin.register(VideoCompletion)
class VideoCompletionAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson_video', 'completed_at')
    list_filter = ('user',)
    ordering = ('-completed_at',)
