from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from .forms import RegistrationForm, LogInForm, UpdateProfileForm, UpdatePasswordForm, PickupArrangementForm, ForgotPasswordForm
from utils import utilities
from user.models import User, Role
from shared_zone.models import SharedZone
from request.models import Notification
from django.http import HttpResponseForbidden
from django.contrib import messages
import datetime
from django.db.models import Q  # for making queries
from tool_sharing.settings import ADMIN_CODE
from request.models import Request
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import string
import random
from manage_tools.models import Tool
from tool_sharing.settings import DEFAULT_FROM_EMAIL


def sig_up(request):
    if utilities.is_user_logged_in(session=request.session):
        return redirect(reverse('index'))
    title = "Sign Up"
    button_title = "Sign Up"
    form = RegistrationForm(request.POST or None)
    context = {
        "title": title,
        "form": form,
        "button_title": button_title
    }
    if request.method == 'POST':
        if form.is_valid():
            user = form.save(commit=False)
            user.password = utilities.hash_password(user.password)
            is_shared_zone = SharedZone.objects.filter(zipcode=user.zipcode, enabled=1).exists()
            try:
                role = Role.objects.get(code=Role.USER)
                user.role = role
            except Role.DoesNotExist:
                pass
            if is_shared_zone:
                user.shared_zone = SharedZone.objects.get(zipcode=user.zipcode)
                request.session['is_shared_zone'] = True
            user.save()
            notification = Notification(user=user)
            notification.save()

            try:
                utilities.send_email('registration.txt', 'registration.html', {'url': "http://localhost:8000", 'email': DEFAULT_FROM_EMAIL}, "Welcome to Tool Sharing", user.email)
            except Exception as e:
                print(e)

            request.session['cool_user'] = user.id
            request.session['cool_user_name'] = user.last_name + ", " + user.first_name
            if user.role is not None:
                request.session['user_role'] = user.role.code

            # Display the user a success message
            messages.success(request, 'Your account registered successfully')

            if not is_shared_zone:
                return redirect(reverse('shared_zone:index'))
            return redirect(reverse('index'))
    return render(request, "user/user_detail.html", context)


def sign_in(request):
    if request.method == 'GET':
        if utilities.is_user_logged_in(session=request.session):
            user = User.objects.get(id=request.session["cool_user"], enabled=1)
            if not SharedZone.objects.filter(zipcode=user.zipcode, enabled=1).exists():
                return redirect(reverse('shared_zone:index'))
            request.session['is_shared_zone'] = True
            return redirect(reverse('index'))
    title = "Sign In"
    form = LogInForm(request.POST or None)
    context = {
        "title": title,
        "form": form
    }
    if request.method == 'POST':
        if form.is_valid():

            user = User.objects.get(email=form.cleaned_data["email"], enabled=1)
            request.session['cool_user'] = user.id
            request.session['cool_user_name'] = user.last_name + ", " + user.first_name

            is_shared_zone = SharedZone.objects.filter(zipcode=user.zipcode, enabled=1).exists()
            if not is_shared_zone:
                return redirect(reverse('shared_zone:index'))
            if not user.shared_zone:
                user.shared_zone = SharedZone.objects.get(zipcode=user.zipcode, enabled=1)
                user.save()
            request.session['is_shared_zone'] = True

            # The promote coordinator session to control the menu item
            request.session['user_role'] = user.role.code

            try:
                notification = Notification.objects.get(user=user)
            except Notification.DoesNotExist:
                notification = Notification(user=user)
                notification.save()
            if notification.pending_received > 0:
                request.session['notification_r'] = notification.pending_received
            if notification.pending_sent > 0:
                request.session['notification_s'] = notification.pending_sent
            return redirect(reverse('index'))
    return render(request, "user/sing_in.html", context)


def log_out(request):
    try:
        del request.session['cool_user']
    except KeyError:
        pass
    try:
        del request.session['is_shared_zone']
    except KeyError:
        pass
    try:
        del request.session['cool_user_name']
    except KeyError:
        pass
    try:
        del request.session['user_role']
    except KeyError:
        pass
    try:
        del request.session['notification_s']
    except KeyError:
        pass
    try:
        del request.session['notification_r']
    except KeyError:
        pass
    return redirect(reverse('sign_in'))


def my_profile(request):
    if not utilities.is_user_logged_in(session=request.session):
        return redirect(reverse('sign_in'))
    user = User.objects.get(id=request.session["cool_user"])
    return render(request, "user/my_profile.html", {"my_profile": True, "title": "Update Profile", "user": user})


def update_profile(request):
    if not utilities.is_user_logged_in(session=request.session):
        return redirect(reverse('sign_in'))
    if request.method == 'GET':
        user = User.objects.get(id=request.session["cool_user"])
        form = UpdateProfileForm(request.POST or None, instance=user)
    if request.method == 'POST':
        user = User.objects.get(id=request.session["cool_user"])
        old_zipcode = user.zipcode
        form = UpdateProfileForm(request.POST or None, instance=user)
        if form.is_valid():
            if user.zipcode != old_zipcode and Tool.objects.filter(owner=user, status=Tool.BORROWED, enabled=True).count() > 0:
                context = {
                    "title": "Update Profile",
                    "form": form,
                    "button_title": "Save",
                    "my_profile": True,
                    "update": True,
                    'error_message': "You cannot change your zipcode. You have borrowed tools."
                }
                return render(request, "user/user_detail.html", context)
            elif user.zipcode != old_zipcode and Tool.objects.filter(owner=user, shared_from=Tool.SHED, enabled=True).count() > 0:
                context = {
                    "title": "Update Profile",
                    "form": form,
                    "button_title": "Save",
                    "my_profile": True,
                    "update": True,
                    'error_message': "You cannot change your zipcode. You have tools in the Community Shed."
                }
                return render(request, "user/user_detail.html", context)
            elif user.is_admin() and user.zipcode != old_zipcode and User.objects.filter(zipcode=user.zipcode, role=user.role).exclude(pk=user.id).count() == 0:
                context = {
                    "title": "Update Profile",
                    "form": form,
                    "button_title": "Save",
                    "my_profile": True,
                    "update": True,
                    'error_message': "You are the only Administrator is this Shared Zone. Please promote someone else to Administrator before changing your zipcode."
                }
                return render(request, "user/user_detail.html", context)
            user = form.save(commit=False)
            request.session['cool_user_name'] = user.last_name + ", " + user.first_name
            if SharedZone.objects.filter(zipcode=user.zipcode, enabled=1).exists():
                user.shared_zone = SharedZone.objects.get(zipcode=user.zipcode, enabled=1)
                user.role = Role.objects.get(code="USER")
                user.save()
            else:
                user.shared_zone = None
                user.save()
                return redirect(reverse('shared_zone:index'))
            messages.success(request, 'Your profile was updated successfully.')
            return redirect(reverse('user:my_profile'))
    context = {
        "title": "Update Profile",
        "form": form,
        "button_title": "Save",
        "my_profile": True,
        "update": True
    }
    return render(request, "user/user_detail.html", context)


# here is the code for changing the password
def change_password(request):
    if not utilities.is_user_logged_in(session=request.session):
        return redirect(reverse('sign_in'))
    title = "Change Password"
    form = UpdatePasswordForm(request.POST or None)
    success = None

    if request.method == 'POST':
        user = User.objects.get(id=request.session["cool_user"], enabled=1)
        form.set_current_password(user.password)
        if form.is_valid():
            user.password = utilities.hash_password(form.cleaned_data["new_password"])  # change password to hash
            user.save()
            success = True
    context = {
        "title": title,
        "my_profile": True,
        "form": form,
        "success": success
    }

    return render(request, "user/change_password.html", context)


def pickup_arrangement(request):
    if not utilities.is_user_logged_in(session=request.session):
        return redirect(reverse('sign_in'))

    user = User.objects.get(id=request.session["cool_user"], enabled=1)
    form = PickupArrangementForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            pickup_days = ' '.join(request.POST.getlist('days'))
            pickup_times = request.POST.get('time_from') + " - " + request.POST.get('time_to')
            user.pickup_days = pickup_days
            user.pickup_times = pickup_times
            user.save()
            messages.success(request, 'Your changes saved successfully.')
        else:
            pickup_days = request.POST.getlist('days')
            pickup_times = [request.POST.get('time_from'), request.POST.get('time_to')]
            return render(request, "user/pickup_arrangement.html", {"title": "Pickup Time", 'form': form,
                                                                    'pickup_days': pickup_days,
                                                                    'pickup_times': pickup_times,
                                                                    'my_profile': True})

    pickup_days = user.pickup_days.split() if user.pickup_days else []
    pickup_times = user.pickup_times.split(' - ') if user.pickup_times else []

    context = {"title": "Pickup Time", 'form': form, 'pickup_days': pickup_days, 'pickup_times': pickup_times,
               'my_profile': True}

    return render(request, "user/pickup_arrangement.html", context)


def promote_coordinator(request, search_term=""):
    if not utilities.is_user_logged_in(session=request.session):
        return redirect(reverse('sign_in'))
    if 'is_shared_zone' not in request.session:
        return redirect(reverse('shared_zone:index'))

    user = User.objects.get(id=request.session["cool_user"], enabled=1)

    # only admins are allowed to make users admin
    if user.role.code != ADMIN_CODE:
        return HttpResponseForbidden()

    admins_in_zone = User.objects.filter(Q(shared_zone=user.shared_zone),
                                         Q(role__code=ADMIN_CODE),
                                         Q(first_name__icontains=search_term) |
                                         Q(email__icontains=search_term) |
                                         Q(last_name__icontains=search_term)).order_by('role_date')

    users_in_zone = User.objects.filter(Q(shared_zone=user.shared_zone),
                                        Q(role__code=Role.USER),
                                        Q(first_name__icontains=search_term) |
                                        Q(email__icontains=search_term) |
                                        Q(last_name__icontains=search_term))

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            new_user = User.objects.get(pk=user_id)

            if request.POST.get('cancel_admin_operation'):
                if User.objects.filter(zipcode=new_user.zipcode, role=new_user.role).exclude(pk=user.id).count() == 0:
                    messages.error(request,
                                   "You are the only Administrator is this Shared Zone. Please promote someone else to Administrator first!")
                    return redirect(reverse('user:promote_coordinator'))
                new_user.role = Role.objects.get(code=Role.USER)
                messages.success(request, "The user was removed from coordination successfully!")
                new_user.role_date = datetime.datetime.now()
                messages.warning(request, None)
                new_user.save()
                if new_user.id == user.id:
                    request.session['user_role'] = new_user.role.code
                    return redirect('/')
                else:
                    return redirect(reverse('user:promote_coordinator'))

            else:
                new_user.role = Role.objects.get(code=Role.ADMIN)
                messages.success(request, "The user was promoted to coordinator successfully!")
                new_user.role_date = datetime.datetime.now()
                new_user.save()
                return redirect(reverse('user:promote_coordinator'))

        except User.DoesNotExist:
            messages.warning(request, 'The user does not exist!')
    return render(request, 'user/promote_coordinator.html',
                  {"title": "Promote Coordinator", 'users_in_zone': users_in_zone, 'admins_in_zone': admins_in_zone,
                   'promote_coordinator': True, 'search_term': search_term})


def history(request):
    if not utilities.is_user_logged_in(session=request.session):
        return redirect(reverse('sign_in'))
    if 'is_shared_zone' not in request.session:
        return redirect(reverse('shared_zone:index'))
    borrowing_history = Request.objects.filter((Q(borrower=request.session["cool_user"]) & Q(borrower_enabled=False))
                                               | (Q(lender=request.session["cool_user"]) & Q(lender_enabled=False))).order_by('-date')

    paginator = Paginator(borrowing_history, 10)
    page = request.GET.get('page')
    try:
        borrowing_history = paginator.page(page)
    except PageNotAnInteger:
        borrowing_history = paginator.page(1)
    except EmptyPage:
        borrowing_history = paginator.page(paginator.num_pages)

    return render(request, "user/history.html", {'my_profile': True, 'history': borrowing_history})


def forgot_password(request):
    if utilities.is_user_logged_in(session=request.session):
        return redirect(reverse('index'))
    form = ForgotPasswordForm(request.POST or None)
    context = {}
    if request.method == 'POST':
        if form.is_valid():
            email = form.clean_email()
            try:
                user = User.objects.get(email=email, enabled=True)
                password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
                user.password = utilities.hash_password(password)
                user.save()

                try:
                    utilities.send_email('forgot_password.txt', 'forgot_password.html', {'password': password}, "Password Reset", email)
                except Exception as e:
                    print(e)

                context['message'] = "A message was sent to your email with instructions for resetting the password."
            except Exception as e:
                print(e)
    context['form'] = form
    return render(request, "user/forgot_password.html", context)
