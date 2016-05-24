from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from user.models import User, Role
from shared_zone.models import SharedZone
from utils.utilities import is_user_logged_in


def index(request):

    role = Role()
    role.post_roles()

    if is_user_logged_in(session=request.session):
        user = User.objects.get(id=request.session["cool_user"], enabled=1)
        if not SharedZone.objects.filter(zipcode=user.zipcode, enabled=1).exists():
            return redirect(reverse('shared_zone:index'))
        request.session['is_shared_zone'] = True

        return redirect(reverse('share_statistics:individual_statistics'))
    else:
        return render(request, "home.html", {'title': 'Welcome'})
