from django.urls import path
from . import views

urlpatterns = [
    # Auth API
    path('login/', views.login_view, name='api-login'),
    path('logout/', views.logout_view, name='api-logout'),
    path('logout/template/', views.logout_template_view, name='logout-template'),
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
    path('dashboard/student/', views.student_dashboard_updated, name='student_dashboard'),
    path('dashboard/student/emploi/', views.student_schedule, name='student_schedule'),
    path('dashboard/student/profile/', views.student_profile, name='student_profile'),
    
    # Classes & Groupes
    path('dashboard/admin/classes/', views.admin_gestion_classes, name='admin_gestion_classes'),
    path('api/classes/', views.api_classes_list, name='api_classes_list'),
    path('api/groupes/', views.api_groupes_list, name='api_groupes_list'),
    path('api/affecter-groupe/', views.api_affecter_groupe, name='api_affecter_groupe'),
    
    # ═══════════════════════════════════════════════════════════════════════
    # LMS URLS
    # ═══════════════════════════════════════════════════════════════════════
    
    # Admin LMS Management
    path('dashboard/admin/courses/', views.admin_courses_list, name='admin_courses_list'),
    path('dashboard/admin/courses/<int:course_id>/edit/', views.admin_course_edit, name='admin_course_edit'),
    path('dashboard/admin/courses/<int:course_id>/delete/', views.admin_course_delete, name='admin_course_delete'),
    path('dashboard/admin/courses/<int:course_id>/lessons/', views.admin_course_lessons, name='admin_course_lessons'),
    path('dashboard/admin/courses/<int:course_id>/enrollments/', views.admin_course_enrollments, name='admin_course_enrollments'),
    path('dashboard/admin/enrollments/', views.admin_all_enrollments, name='admin_all_enrollments'),
    path('dashboard/admin/certificates/', views.admin_all_certificates, name='admin_all_certificates'),
    path('dashboard/admin/student-of-month/', views.admin_student_of_month, name='admin_student_of_month'),
    path('dashboard/admin/student-of-month/calculate/', views.admin_calculate_som, name='admin_calculate_som'),
    
    # Teacher LMS
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/teacher/profile/', views.teacher_profile, name='teacher_profile'),
    path('dashboard/teacher/courses/', views.teacher_courses, name='teacher_courses'),
    path('dashboard/teacher/courses/create/', views.teacher_course_create, name='teacher_course_create'),
    path('dashboard/teacher/courses/<int:course_id>/edit/', views.teacher_course_edit, name='teacher_course_edit'),
    path('dashboard/teacher/courses/<int:course_id>/delete/', views.teacher_course_delete, name='teacher_course_delete'),
    path('dashboard/teacher/courses/<int:course_id>/lessons/', views.teacher_course_lessons, name='teacher_course_lessons'),
    path('dashboard/teacher/courses/<int:course_id>/lessons/create/', views.teacher_lesson_create, name='teacher_lesson_create'),
    path('dashboard/teacher/courses/<int:course_id>/lessons/<int:lesson_id>/edit/', views.teacher_lesson_edit, name='teacher_lesson_edit'),
    path('dashboard/teacher/courses/<int:course_id>/lessons/<int:lesson_id>/delete/', views.teacher_lesson_delete, name='teacher_lesson_delete'),
    path('dashboard/teacher/courses/<int:course_id>/enrollments/', views.teacher_course_enrollments, name='teacher_course_enrollments'),
    
    # Student LMS
    path('dashboard/student/courses/', views.student_courses_browse, name='student_courses_browse'),
    path('dashboard/student/courses/<int:course_id>/', views.student_course_detail, name='student_course_detail'),
    path('dashboard/student/courses/<int:course_id>/enroll/', views.student_course_enroll, name='student_course_enroll'),
    path('dashboard/student/my-courses/', views.student_my_courses, name='student_my_courses'),
    path('dashboard/student/my-courses/<int:course_id>/learn/', views.student_course_learn, name='student_course_learn'),
    path('dashboard/student/my-courses/<int:course_id>/lessons/<int:lesson_id>/complete/', views.student_lesson_complete, name='student_lesson_complete'),
    path('dashboard/student/video-complete/', views.student_video_complete, name='student_video_complete'),
    path('dashboard/student/courses/<int:course_id>/certificate/', views.course_certificate_pdf, name='course_certificate_pdf'),
    path('dashboard/student/certificates/', views.student_my_certificates, name='student_my_certificates'),
    path('dashboard/student/certificates/<int:certificate_id>/', views.student_certificate_view, name='student_certificate_view'),
    
    # LMS API Endpoints
    path('api/courses/<int:course_id>/enroll/', views.api_enroll_course, name='api_enroll_course'),
    path('api/lessons/<int:lesson_id>/complete/', views.api_complete_lesson, name='api_complete_lesson'),
    path('api/courses/<int:course_id>/progress/', views.api_get_progress, name='api_get_progress'),
    path('api/student-of-month/', views.api_get_student_of_month, name='api_get_student_of_month'),

    # ═══════════════════════════════════════════════════════════════════════
    # CV MAKER URLS
    # ═══════════════════════════════════════════════════════════════════════
    path('dashboard/cv/', views.cv_list, name='cv_list'),
    path('dashboard/cv/create/', views.cv_create, name='cv_create'),
    path('dashboard/cv/<int:id>/edit/', views.cv_edit, name='cv_edit'),
    path('dashboard/cv/<int:id>/download/pdf/', views.cv_download_pdf, name='cv_download_pdf'),
    path('dashboard/cv/<int:id>/download/docx/', views.cv_download_docx, name='cv_download_docx'),
    path('dashboard/cv/<int:id>/delete/', views.cv_delete, name='cv_delete'),
    path('dashboard/cv/<int:id>/clone/', views.cv_clone, name='cv_clone'),

    # ═══════════════════════════════════════════════════════════════════════
    # CHAT PUBLIC URLS
    # ═══════════════════════════════════════════════════════════════════════
    path('dashboard/chat/', views.chat_page, name='chat_page'),
    path('dashboard/chat/send/', views.chat_send, name='chat_send'),
    path('dashboard/chat/messages/', views.chat_messages, name='chat_messages'),
    path('dashboard/chat/delete/<int:message_id>/', views.chat_delete, name='chat_delete'),
    path('dashboard/chat/ban/<int:user_id>/', views.chat_ban, name='chat_ban'),
    path('dashboard/chat/unban/<int:user_id>/', views.chat_unban, name='chat_unban'),

    # ═══════════════════════════════════════════════════════════════════════
    # FRIEND SYSTEM & PRIVATE MESSAGING URLS
    # ═══════════════════════════════════════════════════════════════════════
    path('dashboard/chat/friend-request/<int:user_id>/', views.chat_friend_request, name='chat_friend_request'),
    path('dashboard/chat/friend-request/<int:request_id>/accept/', views.chat_friend_accept, name='chat_friend_accept'),
    path('dashboard/chat/friend-request/<int:request_id>/decline/', views.chat_friend_decline, name='chat_friend_decline'),
    path('dashboard/chat/invitations/', views.chat_invitations, name='chat_invitations'),
    path('dashboard/chat/block/<int:user_id>/', views.chat_block_user, name='chat_block_user'),
    path('dashboard/chat/private/<int:user_id>/', views.chat_private, name='chat_private'),
    path('dashboard/chat/friends/', views.chat_friends_json, name='chat_friends_json'),
]
