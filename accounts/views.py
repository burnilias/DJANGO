import json
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password, check_password
from .models import CustomUser, Classe, Groupe
from .decorators import login_required_custom, role_required, _get_token_user, session_login_required, session_role_required


# ── Helpers ─────────────────────────────────────────────────────────────────

def _user_to_dict(user):
    """Serialise a CustomUser the way the frontend expects."""
    return {
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'name': user.name,
        'role': user.role,
        'status': user.status,
        'is_active': user.status == 'active',
        'phone': user.phone,
        'bio': user.bio,
        'created_at': user.created_at.isoformat() if user.created_at else None,
    }


def _parse_json(request):
    try:
        return json.loads(request.body)
    except Exception:
        return {}


# ── Login ──────────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(['POST'])
def login_view(request):
    data = _parse_json(request)
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''

    if not email or not password:
        return JsonResponse(
            {'success': False, 'message': 'Email et mot de passe requis.'},
            status=400,
        )

    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return JsonResponse(
            {'success': False, 'message': 'Email ou mot de passe incorrect.'},
            status=401,
        )

    if not user.check_password(password):
        return JsonResponse(
            {'success': False, 'message': 'Email ou mot de passe incorrect.'},
            status=401,
        )

    if user.status == 'desactive':
        return JsonResponse(
            {'success': False, 'message': 'Ce compte est désactivé.'},
            status=403,
        )

    if user.status == 'veille':
        return JsonResponse(
            {'success': False, 'message': 'Ce compte est en veille.'},
            status=403,
        )

    # Create / retrieve DRF Token
    token, _ = Token.objects.get_or_create(user=user)

    # Also store in Django session (spec requirement)
    request.session['user_id'] = user.id
    request.session['role'] = user.role
    request.session['name'] = user.name
    request.session['first_name'] = user.first_name
    request.session['last_name'] = user.last_name

    return JsonResponse({
        'success': True,
        'token': token.key,
        'user': _user_to_dict(user),
        'role': user.role,
        'message': 'Authentication successful',
    })


# ── Logout ──────────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(['POST'])
def logout_view(request):
    user = _get_token_user(request)
    if user:
        try:
            Token.objects.filter(user=user).delete()
        except Exception:
            pass
    request.session.flush()
    return JsonResponse({'success': True, 'message': 'Logged out successfully.'})


# ── Profile ─────────────────────────────────────────────────────────────────

@login_required_custom
@require_http_methods(['GET'])
def profile_view(request):
    user = request.custom_user
    return JsonResponse({
        'success': True,
        'user': _user_to_dict(user),
        'role': user.role,
    })


# ── Admin: List Users ─────────────────────────────────────────────────────

@login_required_custom
@role_required('admin')
@require_http_methods(['GET'])
def admin_users_list(request):
    users = CustomUser.objects.all().order_by('-created_at')
    return JsonResponse({
        'success': True,
        'users': [_user_to_dict(u) for u in users],
    })


# ── Admin: Create User ─────────────────────────────────────────────────────

@csrf_exempt
@login_required_custom
@role_required('admin')
@require_http_methods(['POST'])
def admin_user_create(request):
    data = _parse_json(request)
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''
    first_name = (data.get('first_name') or '').strip()
    last_name = (data.get('last_name') or '').strip()
    role = data.get('role', 'student')
    phone = data.get('phone', '')
    bio = data.get('bio', '')

    if not email or not password or not first_name or not last_name:
        return JsonResponse(
            {'success': False, 'message': 'Email, password, first name and last name are required.'},
            status=400,
        )

    if role not in ('admin', 'teacher', 'student'):
        return JsonResponse(
            {'success': False, 'message': 'Invalid role.'},
            status=400,
        )

    if CustomUser.objects.filter(email=email).exists():
        return JsonResponse(
            {'success': False, 'message': 'A user with this email already exists.'},
            status=400,
        )

    user = CustomUser(
        email=email,
        first_name=first_name,
        last_name=last_name,
        role=role,
        phone=phone,
        bio=bio,
        status='active',
    )
    user.set_password(password)
    user.save()

    return JsonResponse({
        'success': True,
        'message': 'User created successfully.',
        'user': _user_to_dict(user),
    })


# ── Admin: Update User ─────────────────────────────────────────────────────

@csrf_exempt
@login_required_custom
@role_required('admin')
@require_http_methods(['PUT', 'PATCH'])
def admin_user_update(request, user_id):
    try:
        target = CustomUser.objects.get(pk=user_id)
    except CustomUser.DoesNotExist:
        return JsonResponse(
            {'success': False, 'message': 'User not found.'},
            status=404,
        )

    admin = request.custom_user

    # Safety: admin cannot change their own role or status
    if admin.id == target.id:
        data = _parse_json(request)
        if 'role' in data and data['role'] != admin.role:
            return JsonResponse(
                {'success': False, 'message': 'You cannot change your own role.'},
                status=403,
            )
        # Map is_active back to status
        new_status = _map_is_active_to_status(data)
        if new_status and new_status != admin.status:
            return JsonResponse(
                {'success': False, 'message': 'You cannot change your own status.'},
                status=403,
            )

    data = _parse_json(request)

    if 'email' in data:
        target.email = data['email'].strip()
    if 'first_name' in data:
        target.first_name = data['first_name'].strip()
    if 'last_name' in data:
        target.last_name = data['last_name'].strip()
    if 'role' in data:
        if data['role'] not in ('admin', 'teacher', 'student'):
            return JsonResponse(
                {'success': False, 'message': 'Invalid role.'},
                status=400,
            )
        target.role = data['role']
    if 'phone' in data:
        target.phone = data['phone']
    if 'bio' in data:
        target.bio = data['bio']

    # Map is_active (boolean from frontend) → status field
    new_status = _map_is_active_to_status(data)
    if new_status:
        target.status = new_status

    # Optional password change
    if data.get('password'):
        target.set_password(data['password'])

    target.save()

    return JsonResponse({
        'success': True,
        'message': 'User updated successfully.',
        'user': _user_to_dict(target),
    })


def _map_is_active_to_status(data):
    """Convert frontend's is_active boolean to our status string."""
    if 'is_active' in data:
        return 'active' if data['is_active'] else 'desactive'
    if 'status' in data:
        return data['status']
    return None


# ── Admin: Delete User ─────────────────────────────────────────────────────

@csrf_exempt
@login_required_custom
@role_required('admin')
@require_http_methods(['DELETE'])
def admin_user_delete(request, user_id):
    admin = request.custom_user

    if admin.id == int(user_id):
        return JsonResponse(
            {'success': False, 'message': 'You cannot delete your own account.'},
            status=403,
        )

    try:
        target = CustomUser.objects.get(pk=user_id)
    except CustomUser.DoesNotExist:
        return JsonResponse(
            {'success': False, 'message': 'User not found.'},
            status=404,
        )

    target.delete()
    return JsonResponse({
        'success': True,
        'message': 'User deleted successfully.',
    })


# ══════════════════════════════════════════════════════════════════════════
# ADMIN DASHBOARD — Django Template Views (session-based auth)
# ══════════════════════════════════════════════════════════════════════════

@session_login_required
@session_role_required('admin')
def admin_dashboard(request):
    user = request.session_user
    context = {
        'total_users': CustomUser.objects.count(),
        'total_admins': CustomUser.objects.filter(role='admin').count(),
        'total_teachers': CustomUser.objects.filter(role='teacher').count(),
        'total_students': CustomUser.objects.filter(role='student').count(),
        'recent_users': CustomUser.objects.order_by('-created_at')[:5],
        'active_count': CustomUser.objects.filter(status='active').count(),
        'desactive_count': CustomUser.objects.filter(status='desactive').count(),
        'veille_count': CustomUser.objects.filter(status='veille').count(),
        'session_user': user,
        'page_title': 'Dashboard',
    }
    return render(request, 'admin/dashboard.html', context)


@session_login_required
@session_role_required('admin')
def admin_user_list(request):
    user = request.session_user
    search = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')

    qs = CustomUser.objects.all()
    if search:
        qs = qs.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    if role_filter:
        qs = qs.filter(role=role_filter)
    if status_filter:
        qs = qs.filter(status=status_filter)
    qs = qs.order_by('-created_at')

    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search': search,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'session_user': user,
        'page_title': 'Utilisateurs',
        'groupes': Groupe.objects.select_related('classe').all().order_by('classe__nom', 'nom'),
    }
    return render(request, 'admin/users/list.html', context)


@session_login_required
@session_role_required('admin')
def admin_add_user(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        bio = request.POST.get('bio', '').strip()
        role = request.POST.get('role', 'student')
        status = request.POST.get('status', 'active')
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        errors = {}
        if not first_name:
            errors['first_name'] = 'Le prénom est requis.'
        if not last_name:
            errors['last_name'] = 'Le nom est requis.'
        if not email:
            errors['email'] = "L'email est requis."
        elif CustomUser.objects.filter(email=email).exists():
            errors['email'] = 'Un utilisateur avec cet email existe déjà.'
        if not password:
            errors['password'] = 'Le mot de passe est requis.'
        elif len(password) < 8:
            errors['password'] = 'Le mot de passe doit contenir au moins 8 caractères.'
        if password != password_confirm:
            errors['password_confirm'] = 'Les mots de passe ne correspondent pas.'
        if role not in ('admin', 'teacher', 'student'):
            errors['role'] = 'Rôle invalide.'
        if status not in ('active', 'desactive', 'veille'):
            errors['status'] = 'Statut invalide.'

        if errors:
            # Return JSON for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': errors}, status=400)
            return render(request, 'admin/users/add.html', {
                'errors': errors,
                'form_data': request.POST,
                'session_user': request.session_user,
                'page_title': 'Ajouter un utilisateur',
            })

        groupe_id = request.POST.get('groupe_id', '') or None
        new_user = CustomUser(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            bio=bio,
            role=role,
            status=status,
            groupe_id=groupe_id,
        )
        new_user.set_password(password)
        new_user.save()
        
        # Return JSON for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Utilisateur créé avec succès.'})
        
        messages.success(request, 'Utilisateur créé avec succès.')
        return redirect('admin_user_list')

    # GET request - redirect to user list (modal handles the form now)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Method not allowed.'}, status=405)
    
    return render(request, 'admin/users/add.html', {
        'session_user': request.session_user,
        'page_title': 'Ajouter un utilisateur',
    })


@session_login_required
@session_role_required('admin')
def admin_edit_user(request, id):
    target = get_object_or_404(CustomUser, id=id)
    admin_user = request.session_user

    if request.method == 'GET':
        return JsonResponse({
            'id': target.id,
            'first_name': target.first_name,
            'last_name': target.last_name,
            'email': target.email,
            'phone': target.phone,
            'bio': target.bio,
            'role': target.role,
            'status': target.status,
            'is_self': admin_user.id == target.id,
        })

    # POST
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    bio = request.POST.get('bio', '').strip()
    role = request.POST.get('role', target.role)
    status = request.POST.get('status', target.status)
    new_password = request.POST.get('new_password', '')
    new_password_confirm = request.POST.get('new_password_confirm', '')

    errors = {}
    if not first_name:
        errors['first_name'] = 'Le prénom est requis.'
    if not last_name:
        errors['last_name'] = 'Le nom est requis.'
    if not email:
        errors['email'] = "L'email est requis."
    elif CustomUser.objects.filter(email=email).exclude(id=target.id).exists():
        errors['email'] = 'Un utilisateur avec cet email existe déjà.'

    # Admin cannot change own role/status
    is_self = admin_user.id == target.id
    if is_self:
        role = target.role
        status = target.status
    else:
        if role not in ('admin', 'teacher', 'student'):
            errors['role'] = 'Rôle invalide.'
        if status not in ('active', 'desactive', 'veille'):
            errors['status'] = 'Statut invalide.'

    if new_password:
        if len(new_password) < 8:
            errors['new_password'] = 'Le mot de passe doit contenir au moins 8 caractères.'
        if new_password != new_password_confirm:
            errors['new_password_confirm'] = 'Les mots de passe ne correspondent pas.'

    if errors:
        return JsonResponse({'success': False, 'errors': errors}, status=400)

    target.first_name = first_name
    target.last_name = last_name
    target.email = email
    target.phone = phone
    target.bio = bio
    target.role = role
    target.status = status
    if new_password:
        target.set_password(new_password)
    target.save()

    return JsonResponse({'success': True, 'message': 'Utilisateur mis à jour.'})


@session_login_required
@session_role_required('admin')
def admin_delete_user(request, id):
    admin_user = request.session_user
    if admin_user.id == id:
        messages.error(request, 'Vous ne pouvez pas supprimer votre propre compte.')
        return redirect('admin_user_list')

    target = get_object_or_404(CustomUser, id=id)
    # Delete token first to avoid FK constraint error
    Token.objects.filter(user=target).delete()
    target.delete()
    messages.success(request, 'Utilisateur supprimé.')
    return redirect('admin_user_list')


@session_login_required
@session_role_required('admin')
def admin_change_status(request, id):
    admin_user = request.session_user
    if admin_user.id == id:
        return JsonResponse({'success': False, 'error': 'Vous ne pouvez pas modifier votre propre statut.'}, status=403)

    target = get_object_or_404(CustomUser, id=id)
    if request.method == 'POST':
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        new_status = data.get('new_status', '')
        if new_status not in ('active', 'desactive', 'veille'):
            return JsonResponse({'success': False, 'error': 'Statut invalide.'}, status=400)
        target.status = new_status
        target.save()
        return JsonResponse({'success': True, 'new_status': new_status})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée.'}, status=405)


@session_login_required
@session_role_required('admin')
def admin_profile(request):
    user = request.session_user
    # Refresh from DB
    user = CustomUser.objects.get(pk=user.id)

    if request.method == 'POST':
        form_type = request.POST.get('form_type', '')

        if form_type == 'update_info':
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            phone = request.POST.get('phone', '').strip()
            bio = request.POST.get('bio', '').strip()
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            user.phone = phone
            user.bio = bio
            user.save()
            # Update session
            request.session['first_name'] = user.first_name
            request.session['last_name'] = user.last_name
            messages.success(request, 'Profil mis à jour.')
            return redirect('admin_profile')

        elif form_type == 'change_password':
            current_password = request.POST.get('current_password', '')
            new_password = request.POST.get('new_password', '')
            new_password_confirm = request.POST.get('new_password_confirm', '')

            if not user.check_password(current_password):
                messages.error(request, 'Mot de passe actuel incorrect.')
            elif len(new_password) < 8:
                messages.error(request, 'Le nouveau mot de passe doit contenir au moins 8 caractères.')
            elif new_password != new_password_confirm:
                messages.error(request, 'Les mots de passe ne correspondent pas.')
            else:
                user.set_password(new_password)
                user.save()
                # Re-create session to avoid session invalidation
                request.session['user_id'] = user.id
                request.session['role'] = user.role
                request.session['first_name'] = user.first_name
                request.session['last_name'] = user.last_name
                messages.success(request, 'Mot de passe mis à jour.')
            return redirect('admin_profile')

    context = {
        'profile_user': user,
        'session_user': user,
        'page_title': 'Mon Profil',
    }
    return render(request, 'admin/profile.html', context)


@session_login_required
@session_role_required('admin')
def admin_settings(request):
    context = {
        'session_user': request.session_user,
        'page_title': 'Paramètres',
    }
    return render(request, 'admin/settings.html', context)


# ══════════════════════════════════════════════════════════════════════════
# EMPLOI DU TEMPS (Schedule)
# ══════════════════════════════════════════════════════════════════════════

@session_login_required
@session_role_required('admin')
def admin_schedule_list(request):
    from .models import Schedule
    from datetime import datetime, timedelta
    user = request.session_user
    
    all_schedules = Schedule.objects.select_related('teacher').all()
    teachers = CustomUser.objects.filter(role='teacher', status='active')
    
    # Get current week dates
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    week_start = monday.strftime('%d %B')
    week_end = (monday + timedelta(days=6)).strftime('%d %B %Y')
    
    # Day mapping
    day_names_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    day_short_fr = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
    today_weekday = today.weekday()  # 0=Monday
    
    # Build day headers
    day_names = []
    for i in range(7):
        date = monday + timedelta(days=i)
        day_names.append({
            'name': day_names_fr[i],
            'short': day_short_fr[i],
            'date': date.strftime('%d'),
            'num': str(i + 1),
            'today': i == today_weekday
        })
    
    # Time slots (8:00 to 20:00, every hour) - 60px per hour = 720px total
    time_slots = []
    for i in range(13):  # 8:00 to 20:00
        hour = 8 + i
        time_slots.append({
            'label': f'{hour:02d}:00',
            'position': i * 60  # 60px per hour
        })
    
    # Build days with their schedules positioned correctly
    days = []
    for day_num in range(1, 8):
        day_schedules = []
        day_is_today = (day_num - 1) == today_weekday
        
        for schedule in all_schedules:
            if int(schedule.day_of_week) == day_num:
                # Calculate position based on time (60px per hour, starting at 8:00)
                start_h = schedule.start_time.hour
                start_m = schedule.start_time.minute
                end_h = schedule.end_time.hour
                end_m = schedule.end_time.minute
                
                # Position from 8:00 (minute 0)
                start_minutes = (start_h - 8) * 60 + start_m
                end_minutes = (end_h - 8) * 60 + end_m
                duration = end_minutes - start_minutes
                
                # Map schedule types to user's CSS classes
                type_class_map = {
                    'cours': 'type-lab',
                    'controle': 'type-lang',
                    'examen': 'type-research',
                    'rattrapage': 'type-research',  # fallback
                }
                type_class = type_class_map.get(schedule.schedule_type, '')
                
                day_schedules.append({
                    'id': schedule.id,
                    'name': schedule.name,
                    'start_time': schedule.start_time,
                    'end_time': schedule.end_time,
                    'room': schedule.room,
                    'teacher': schedule.teacher,
                    'type_label': schedule.get_schedule_type_display() if hasattr(schedule, 'get_schedule_type_display') else schedule.schedule_type,
                    'top': max(0, start_minutes),
                    'height': max(30, duration), # minimum 30px for visibility
                    'type_class': type_class,
                })
        
        days.append({
            'num': str(day_num),
            'today': day_is_today,
            'schedules': day_schedules
        })
    
    context = {
        'day_names': day_names,
        'days': days,
        'time_slots': time_slots,
        'teachers': teachers,
        'week_start': week_start,
        'week_end': week_end,
        'session_user': user,
        'page_title': 'Emploi du temps',
    }
    return render(request, 'admin/emploi/list.html', context)


@session_login_required
@session_role_required('admin')
def admin_schedule_add(request):
    from .models import Schedule
    user = request.session_user
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        room = request.POST.get('room', '').strip()
        day_of_week = request.POST.get('day_of_week', '1')
        start_time = request.POST.get('start_time', '')
        end_time = request.POST.get('end_time', '')
        schedule_type = request.POST.get('schedule_type', 'cours')
        teacher_id = request.POST.get('teacher', '')
        
        errors = {}
        if not name:
            errors['name'] = 'Le nom est requis.'
        if not start_time:
            errors['start_time'] = "L'heure de début est requise."
        if not end_time:
            errors['end_time'] = "L'heure de fin est requise."
        
        if errors:
            teachers = CustomUser.objects.filter(role='teacher', status='active')
            return render(request, 'admin/emploi/add.html', {
                'errors': errors,
                'form_data': request.POST,
                'teachers': teachers,
                'session_user': user,
                'page_title': 'Ajouter un cours',
            })
        
        schedule = Schedule(
            name=name,
            description=description,
            room=room,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            schedule_type=schedule_type,
            teacher_id=teacher_id if teacher_id else None,
        )
        schedule.save()
        messages.success(request, 'Cours ajouté avec succès.')
        return redirect('admin_schedule_list')
    
    teachers = CustomUser.objects.filter(role='teacher', status='active')
    return render(request, 'admin/emploi/add.html', {
        'teachers': teachers,
        'session_user': user,
        'page_title': 'Ajouter un cours',
    })


@session_login_required
@session_role_required('admin')
def admin_schedule_edit(request, id):
    from .models import Schedule
    schedule = get_object_or_404(Schedule, id=id)
    user = request.session_user
    
    if request.method == 'POST':
        schedule.name = request.POST.get('name', '').strip()
        schedule.description = request.POST.get('description', '').strip()
        schedule.room = request.POST.get('room', '').strip()
        schedule.day_of_week = request.POST.get('day_of_week', '1')
        schedule.start_time = request.POST.get('start_time', '')
        schedule.end_time = request.POST.get('end_time', '')
        schedule.schedule_type = request.POST.get('schedule_type', 'cours')
        teacher_id = request.POST.get('teacher', '')
        schedule.teacher_id = teacher_id if teacher_id else None
        schedule.save()
        messages.success(request, 'Cours mis à jour.')
        return redirect('admin_schedule_list')
    
    teachers = CustomUser.objects.filter(role='teacher', status='active')
    return render(request, 'admin/emploi/edit.html', {
        'schedule': schedule,
        'teachers': teachers,
        'session_user': user,
        'page_title': 'Modifier le cours',
    })


@session_login_required
@session_role_required('admin')
def admin_schedule_delete(request, id):
    from .models import Schedule
    schedule = get_object_or_404(Schedule, id=id)
    schedule.delete()
    messages.success(request, 'Cours supprimé.')
    return redirect('admin_schedule_list')


# ══════════════════════════════════════════════════════════════════════════
# STUDENT VIEWS (Readonly)
# ══════════════════════════════════════════════════════════════════════════

@session_login_required
@session_role_required('student')
def student_dashboard(request):
    user = request.session_user
    return render(request, 'student/dashboard.html', {
        'session_user': user,
        'page_title': 'Dashboard Étudiant',
    })


@session_login_required
@session_role_required('student')
def student_schedule(request):
    from .models import Schedule
    from datetime import datetime, timedelta
    user = request.session_user
    
    all_schedules = Schedule.objects.select_related('teacher').all()
    
    # Get current week dates
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    week_start = monday.strftime('%d %B')
    week_end = (monday + timedelta(days=6)).strftime('%d %B %Y')
    
    # Day mapping
    day_names_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    day_short_fr = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
    today_weekday = today.weekday()
    
    # Build day headers
    day_names = []
    for i in range(7):
        date = monday + timedelta(days=i)
        day_names.append({
            'name': day_names_fr[i],
            'short': day_short_fr[i],
            'date': date.strftime('%d'),
            'num': str(i + 1),
            'today': i == today_weekday
        })
    
    # Time slots
    time_slots = []
    for i in range(13):
        hour = 8 + i
        time_slots.append({
            'label': f'{hour:02d}:00',
            'position': i * 60
        })
    
    # Build days with schedules
    days = []
    for day_num in range(1, 8):
        day_schedules = []
        day_is_today = (day_num - 1) == today_weekday
        
        for schedule in all_schedules:
            if int(schedule.day_of_week) == day_num:
                start_h = schedule.start_time.hour
                start_m = schedule.start_time.minute
                end_h = schedule.end_time.hour
                end_m = schedule.end_time.minute
                
                start_minutes = (start_h - 8) * 60 + start_m
                end_minutes = (end_h - 8) * 60 + end_m
                duration = end_minutes - start_minutes
                
                # Map schedule types to user's CSS classes
                type_class_map = {
                    'cours': 'type-lab',
                    'controle': 'type-lang',
                    'examen': 'type-research',
                    'rattrapage': 'type-research',
                }
                type_class = type_class_map.get(schedule.schedule_type, '')
                
                day_schedules.append({
                    'id': schedule.id,
                    'name': schedule.name,
                    'start_time': schedule.start_time,
                    'end_time': schedule.end_time,
                    'room': schedule.room,
                    'teacher': schedule.teacher,
                    'type_label': schedule.get_schedule_type_display() if hasattr(schedule, 'get_schedule_type_display') else schedule.schedule_type,
                    'day_name': day_names_fr[day_num - 1],
                    'top': max(0, start_minutes),
                    'height': max(30, duration),
                    'type_class': type_class,
                })
        
        days.append({
            'num': str(day_num),
            'today': day_is_today,
            'day_name': day_names_fr[day_num - 1],
            'schedules': day_schedules
        })
    
    context = {
        'day_names': day_names,
        'days': days,
        'time_slots': time_slots,
        'week_start': week_start,
        'week_end': week_end,
        'session_user': user,
        'page_title': 'Mon Emploi du temps',
    }
    return render(request, 'student/emploi.html', context)


@session_login_required
@session_role_required('student')
def student_profile(request):
    user = request.session_user
    return render(request, 'student/profile.html', {
        'session_user': user,
        'page_title': 'Mon Profil',
    })


# ── Classes & Groupes API ──
@session_login_required
@session_role_required('admin')
def api_classes_list(request):
    if request.method == 'POST':
        nom = json.loads(request.body).get('nom') if request.content_type == 'application/json' else request.POST.get('nom')
        if nom not in dict(Classe.NOM_CHOICES):
            return JsonResponse({'success': False, 'message': 'Nom invalide.'}, status=400)
        classe = Classe.objects.create(nom=nom)
        return JsonResponse({'success': True, 'message': 'Classe créée.', 'id': classe.id})
    classes = Classe.objects.all().order_by('nom')
    data = [{'id': c.id, 'nom': c.nom, 'groupes_count': c.groupes.count()} for c in classes]
    return JsonResponse({'success': True, 'classes': data})


@session_login_required
@session_role_required('admin')
def api_groupes_list(request):
    if request.method == 'POST':
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        nom = data.get('nom')
        classe_id = data.get('classe_id')
        if not nom or not classe_id:
            return JsonResponse({'success': False, 'message': 'Nom et classe requis.'}, status=400)
        groupe = Groupe.objects.create(nom=nom, classe_id=classe_id)
        return JsonResponse({'success': True, 'message': 'Groupe créé.', 'id': groupe.id})
    classe_id = request.GET.get('classe_id')
    groupes = Groupe.objects.all()
    if classe_id:
        groupes = groupes.filter(classe_id=classe_id)
    groupes = groupes.order_by('classe__nom', 'nom')
    data = [{'id': g.id, 'nom': g.nom, 'classe': g.classe.nom, 'members_count': g.members.count()} for g in groupes]
    return JsonResponse({'success': True, 'groupes': data})


@session_login_required
@session_role_required('admin')
def api_affecter_groupe(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST requis.'}, status=405)
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    user_id = data.get('user_id')
    groupe_id = data.get('groupe_id')
    try:
        user = CustomUser.objects.get(id=user_id)
        if groupe_id:
            groupe = Groupe.objects.get(id=groupe_id)
            user.groupe = groupe
        else:
            user.groupe = None
        user.save()
        return JsonResponse({'success': True, 'message': 'Groupe affecté.'})
    except (CustomUser.DoesNotExist, Groupe.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'Utilisateur ou groupe introuvable.'}, status=404)


@session_login_required
@session_role_required('admin')
def admin_gestion_classes(request):
    classes = Classe.objects.all().order_by('nom')
    groupes = Groupe.objects.select_related('classe').all().order_by('classe__nom', 'nom')
    users = CustomUser.objects.select_related('groupe').filter(role='student').order_by('last_name')
    return render(request, 'admin/classes/gestion_classes.html', {
        'session_user': request.session_user,
        'page_title': 'Classes & Groupes',
        'classes': classes,
        'groupes': groupes,
        'users': users,
    })
