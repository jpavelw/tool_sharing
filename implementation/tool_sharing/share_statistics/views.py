from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from user.models import User
from manage_tools.models import Tool
from request.models import Request
from shared_zone.models import SharedZone
from django.db.models import Count
from utils.utilities import is_user_logged_in
from django.db.models import Q  # for making queries
from functools import reduce
import operator


# community statistics
def community_statistics(request):
    if not is_user_logged_in(session=request.session):
        return redirect(reverse('sign_in'))
    if 'is_shared_zone' not in request.session:
        return redirect(reverse('shared_zone:index'))

    zipcode = User.objects.get(id=request.session["cool_user"]).zipcode

    active_lenders = Request.objects.filter(status=Request.APPROVED, lender__zipcode=zipcode).values_list(
        'lender').annotate(active_lender=Count('lender_id')).order_by('-active_lender')[:10]
    active_lenders = [lender[0] for lender in active_lenders]
    active_lenders = User.objects.filter(pk__in=active_lenders)

    active_borrowers = Request.objects.filter(status=Request.APPROVED, borrower__zipcode=zipcode).values_list(
        'borrower').annotate(active_borrower=Count('borrower_id')).order_by('-active_borrower')[:10]
    active_borrowers = [borrower[0] for borrower in active_borrowers]
    active_borrowers = User.objects.filter(pk__in=active_borrowers)

    other_statistic = individual_statistics_data(zipcode)

    most_used_tools = other_statistic[0]
    recently_used_tools = other_statistic[1]

    

    context = {'active_lenders': active_lenders,
               'active_borrowers': active_borrowers,
               'most_used_tools': most_used_tools,
               'recently_used_tools': recently_used_tools}

    return render(request, "share_statistics/community_statistics.html", context)


def individual_statistics(request, zipcode=None):
    if not is_user_logged_in(session=request.session):
        return redirect(reverse('sign_in'))
    if 'is_shared_zone' not in request.session:
        return redirect(reverse('shared_zone:index'))

    user = User.objects.get(id=request.session["cool_user"], enabled=1)
    individual_statistic = individual_statistics_data(user.zipcode, user.id)

    most_used_tools = individual_statistic[0]
    recently_used_tools = individual_statistic[1]

    shared_zone = SharedZone.objects.get(zipcode = user.zipcode)
    context = {'most_used_tools': most_used_tools,
               'recently_used_tools': recently_used_tools,
               'shared_zone': shared_zone}

    return render(request, "share_statistics/individual_statistics.html", context)


def individual_statistics_data(zipcode, user=None):
    args = reduce(operator.or_, [Q(borrower__zipcode__exact=zipcode)])
    kwargs = {'status__exact': Request.APPROVED, 'lender__zipcode__exact': zipcode}

    if not user is None:
        args = reduce(operator.or_, [Q(lender__id=user), Q(borrower__id=user)])

    # execute query
    most_used_tools = Request.objects.filter(args, **kwargs).values_list('tool').annotate(
        used_tool=Count('tool_id')).order_by('-used_tool')[:10]
    most_used_tools = [tool[0] for tool in most_used_tools]
    most_used_tools = Tool.objects.filter(pk__in=most_used_tools)

    recently_used_tools = Request.objects.filter(args, **kwargs).values_list('tool', 'date').order_by(
        '-date').distinct()[:10]
    recently_used_tools = [tool[0] for tool in recently_used_tools]
    recently_used_tools = Tool.objects.filter(pk__in=recently_used_tools)

    return [most_used_tools, recently_used_tools]
