from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.core.urlresolvers import reverse
from .forms import SharedZoneForm
from user.models import User, Role
from utils.utilities import is_user_logged_in
from tool_sharing.settings import ADMIN_CODE
from .models import SharedZone
from django.shortcuts import redirect
from django.contrib import messages


def index(request):
    if not is_user_logged_in(session=request.session):
        return redirect(reverse('sign_in'))
    user = User.objects.get(id=request.session['cool_user'], enabled=1)
    if SharedZone.objects.filter(zipcode=user.zipcode, enabled=1).exists():
        return redirect(reverse('index'))
    title = "New Shared Zone"
    form = SharedZoneForm(request.POST or None)
    context = {
        "title": title,
        "form": form
    }

    if request.method == "POST":
        form = SharedZoneForm(request.POST)
        if form.is_valid():
            shared_zone = form.save(commit=False)
            shared_zone.zipcode = user.zipcode
            try:
                role = Role.objects.get(code=ADMIN_CODE)
                user.role = role
            except:
                pass
            shared_zone.save()
            user.shared_zone = shared_zone
            user.save()
            request.session['user_role'] = user.role.code
            request.session['is_shared_zone'] = True
            return redirect(reverse('index'))
    return render(request, "shared_zone/shared_zone_detail.html", context)

def update_sharedzone(request):
    if not is_user_logged_in(session=request.session):
        return redirect(reverse('sign_in'))
    user = User.objects.get(id=request.session['cool_user'], enabled=1)

    shared_zone = SharedZone.objects.get(zipcode=user.zipcode, enabled=1)

    if not shared_zone:
        return redirect(reverse('shared_zone:index'))

    # only admins are allowed to make users admin
    if not user.role.code == Role().ADMIN:
        return HttpResponseForbidden()

    title = "Update Shared Zone"
    form = None

    if request.method == "POST":
        form = SharedZoneForm(request.POST)

        if form.is_valid():
            shared_zone.name = form.cleaned_data.get('name')
            shared_zone.address = form.cleaned_data.get('address')
            shared_zone.description = form.cleaned_data.get('description')
            shared_zone.save()
            messages.success(request, 'The share zone information updated successfully')
            return redirect(reverse('shared_zone:update'))
    else:
        initial= {
        'name': shared_zone.name, 
        'address': shared_zone.address, 
        'description': shared_zone.description}
        form = SharedZoneForm(initial)

    context = {
        "title": title,
        "form": form,
        "update_sharedzone": True,
    }

    return render(request, "shared_zone/shared_zone_update.html", context)











