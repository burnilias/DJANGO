from django.urls import path
from . import views

urlpatterns = [
    # Auth API
    path('login/', views.login_view, name='api-login'),
    path('logout/', views.logout_view, name='api-logout'),
    path('profile/', views.profile_view, name='api-profile'),

    # Admin CRUD API
    path('admin/users/', views.admin_users_list, name='admin-users-list'),
    path('admin/users/create/', views.admin_user_create, name='admin-user-create'),
    path('admin/users/<int:user_id>/update/', views.admin_user_update, name='admin-user-update'),
    path('admin/users/<int:user_id>/delete/', views.admin_user_delete, name='admin-user-delete'),

    # Admin Dashboard (Django templates)
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/admin/profile/', views.admin_profile, name='admin_profile'),
    path('dashboard/admin/users/', views.admin_user_list, name='admin_user_list'),
    path('dashboard/admin/users/add/', views.admin_add_user, name='admin_add_user'),
    path('dashboard/admin/users/<int:id>/edit/', views.admin_edit_user, name='admin_edit_user'),
    path('dashboard/admin/users/<int:id>/delete/', views.admin_delete_user, name='admin_delete_user'),
    path('dashboard/admin/users/<int:id>/status/', views.admin_change_status, name='admin_change_status'),
    path('dashboard/admin/settings/', views.admin_settings, name='admin_settings'),
    
    # Emploi du temps (Schedule)
    path('dashboard/admin/emploi/', views.admin_schedule_list, name='admin_schedule_list'),
    path('dashboard/admin/emploi/add/', views.admin_schedule_add, name='admin_schedule_add'),
    path('dashboard/admin/emploi/<int:id>/edit/', views.admin_schedule_edit, name='admin_schedule_edit'),
    path('dashboard/admin/emploi/<int:id>/delete/', views.admin_schedule_delete, name='admin_schedule_delete'),
    
    # Student Dashboard (Readonly)
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/student/emploi/', views.student_schedule, name='student_schedule'),
    path('dashboard/student/profile/', views.student_profile, name='student_profile'),
    
    # Classes & Groupes
    path('dashboard/admin/classes/', views.admin_gestion_classes, name='admin_gestion_classes'),
    path('api/classes/', views.api_classes_list, name='api_classes_list'),
    path('api/groupes/', views.api_groupes_list, name='api_groupes_list'),
    path('api/affecter-groupe/', views.api_affecter_groupe, name='api_affecter_groupe'),
]
