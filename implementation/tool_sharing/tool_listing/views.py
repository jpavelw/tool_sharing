from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from manage_tools.models import Tool, ToolCategory
from shared_zone.models import SharedZone
from user.models import User
from request.models import Request, Notification
# from faker import Faker
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q  # for making queries
from utils.utilities import is_user_logged_in, send_email
from django.http import JsonResponse
from django.core import serializers
from django.conf import settings

"""only available tools can be showed
   which determined as AV and enabled
   tools which is bit flag
"""


def index(request):
    if not is_user_logged_in(session=request.session):
        return redirect(reverse('sign_in'))
    if 'is_shared_zone' not in request.session:
        return redirect(reverse('shared_zone:index'))
    # prepare query params
    made_requests = Request.objects.filter(Q(borrower=request.session["cool_user"]), Q(status=Request.PENDING_APPROVAL) | Q(status=Request.APPROVED)).values('tool')
    user = User.objects.get(id=request.session["cool_user"], enabled=1)
    search_term = request.POST['search_term'] if request.POST else ''
    search_category = request.POST['search_category'] if request.POST else ''
    shared_from = request.POST['shared_from'] if request.POST else ''
    tools_list = Tool.objects.filter(
        Q(enabled=1),
        Q(status='AV'),
        Q(name__icontains=search_term) | Q(code__icontains=search_term),
        Q(category__in=ToolCategory.objects.filter(name__startswith=search_category).only(id)),
        Q(shared_from__startswith=shared_from),
        ~Q(owner=user.id),
        Q(owner__zipcode=user.zipcode),
        ~Q(id__in=made_requests)
    )
    paginator = Paginator(tools_list, 12)
    page = request.GET.get('page')
    try:
        tools = paginator.page(page)
    except PageNotAnInteger:
        tools = paginator.page(1)
    except EmptyPage:
        tools = paginator.page(paginator.num_pages)

    return render(request, 'tool_listing/index.html', {
        'tools': tools,
        'categories': category_list,
        'shared_from': Tool().get_all_shared_choices(),
        'borrow': True,
        'search_terms': request.POST,  # return user input
    })

"""The detail information of selected tool
"""


def tool_detail(request, id):
    if not is_user_logged_in(session=request.session):
        return redirect(reverse('sign_in'))
    if 'is_shared_zone' not in request.session:
        return redirect(reverse('shared_zone:index'))

    if request.method == 'GET':
        try:
            tool = Tool.objects.get(id=id, enabled=1)
            pickup_times = User.objects.filter(pk=tool.owner.id).values_list('pickup_days', 'pickup_times')
            pickup_times = list(pickup_times)[0]
            if pickup_times[0] is None or pickup_times[1] is None:
                pickup_times = None
            if tool.is_shared_from_home():
                pickup_address = tool.owner.get_address()
            else:
                pickup_address = SharedZone.objects.get(zipcode=tool.owner.zipcode).address
            may_leave_comment = False
            if Request.objects.filter(borrower=request.session["cool_user"], tool=id, status=Request.RETURNED, may_leave_comment=True).count() > 0:
                may_leave_comment = True
            context = {
                'pickup_address': pickup_address,
                'tool': tool,
                'borrow': True,
                'pickup_times': pickup_times,
                'id': id,
                'may_leave_comment': may_leave_comment
            }
            if "format" in request.GET and request.GET["format"] == "json":
                data = serializers.serialize("json", [tool])
                if pickup_times:
                    pu_times = {
                        'days': pickup_times[0],
                        'hours': pickup_times[1],
                    }
                else:
                    pu_times = None
                response = {'statusCode': 200, 'message': 'OK', 'data': data, 'media': settings.MEDIA_URL, 'pickup_times': pu_times, 'pickup_address': pickup_address}
                return JsonResponse(response)
        except Tool.DoesNotExist:
            context = {
                "not_found": 'The item you requested does not exist',
                'borrow': True,
                'id': id
            }
            if "format" in request.GET and request.GET["format"] == "json":
                response = {'statusCode': 404, 'message': 'The item you requested does not exist'}
                return JsonResponse(response)
        except Exception as e:
            print(e)
    if request.method == 'POST':
        try:
            tool = Tool.objects.get(pk=id, enabled=1)
            borrower = User.objects.get(pk=request.session["cool_user"], enabled=1)
            tool_request = Request(tool=tool, lender=tool.owner, borrower=borrower, zipcode=borrower.zipcode, shared_from=tool.shared_from)
            success_message = "The tool has been requested successfully! Please wait for owner's approval."
            if tool.shared_from == Tool.SHED:
                tool_request.comment = "Borrowing request approved!"
                success_message = "Borrowing request approved!"
                tool_request.status = Request.APPROVED
                tool.status = Tool.BORROWED
                tool.save()
                try:
                    request.session['notification_s'] += 1
                except KeyError:
                    request.session['notification_s'] = 1
                try:
                    optional = "Please return the tool as soon as you finish using it. Remind the shed coordinator to mark the tool as returned."
                    send_email('request_action.txt', 'request_action.html', {'tool_name': tool_request.tool.name, 'request_status': tool_request.get_status_choices(), 'message': tool_request.comment, 'optional': optional}, "Borrowing Request Information", tool_request.borrower.email)
                except Exception as e:
                    print(e)
            tool_request.save()
            if tool_request.tool.shared_from == Tool.HOME:
                try:
                    notification = Notification.objects.get(user=tool.owner)
                except Notification.DoesNotExist:
                    notification = Notification(user=tool.owner)
                    notification.save()
                notification.increment_received()
                notification.save()
                try:
                    send_email('borrowing_request.txt', 'borrowing_request.html', {'borrower': tool_request.borrower.__str__(), 'tool': tool_request.tool.name}, "Borrowing Request Information", tool_request.lender.email)
                except Exception as e:
                    print(e)
            context = {
                'tool': tool,
                'borrow': True,
                'message': success_message,
                'id': id
            }
            if "format" in request.POST and request.POST["format"] == "json":
                response = {'statusCode': 200, 'message': success_message}
                return JsonResponse(response)
        except Tool.DoesNotExist:
            context = {
                "not_found": 'The item you requested does not exist',
                'borrow': True,
                'id': id
            }
            if "format" in request.POST and request.POST["format"] == "json":
                response = {'statusCode': 404, 'message': 'The item you requested does not exist'}
                return JsonResponse(response)
        except Exception as e:
            print(e)
            context = {
                'tool': tool,
                'borrow': True,
                'id': id
            }
    return render(request, 'tool_listing/tool_detail.html', context)

def category_list():
    return ToolCategory.objects.order_by('name')
