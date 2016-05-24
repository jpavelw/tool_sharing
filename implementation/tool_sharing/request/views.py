from django.shortcuts import render
from utils.utilities import is_user_logged_in, send_email
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse, HttpResponseForbidden
from .models import Request, Notification
from django.views.decorators.csrf import csrf_exempt
from user.models import User
from manage_tools.models import Tool
from django.contrib import messages
import datetime


def sent(request):
    if not is_user_logged_in(session=request.session):
        return redirect(reverse('sign_in'))
    if 'is_shared_zone' not in request.session:
        return redirect(reverse('shared_zone:index'))

    try:
        del request.session['notification_s']
        notification = Notification.objects.get(user=request.session["cool_user"])
        notification.pending_sent = 0
        notification.save()
    except KeyError:
        pass
    sent_requests = Request.objects.filter(borrower=request.session["cool_user"], borrower_enabled=True).order_by('-id')

    paginator = Paginator(sent_requests, 10)
    page = request.GET.get('page')
    try:
        sent_requests = paginator.page(page)
    except PageNotAnInteger:
        sent_requests = paginator.page(1)
    except EmptyPage:
        sent_requests = paginator.page(paginator.num_pages)

    context = {
        'sent_requests': sent_requests,
        'my_requests': True
    }
    return render(request, "request/sent_requests.html", context)


def received(request):
    if not is_user_logged_in(session=request.session):
        return redirect(reverse('sign_in'))
    if 'is_shared_zone' not in request.session:
        return redirect(reverse('shared_zone:index'))
    try:
        del request.session['notification_r']
        try:
            notification = Notification.objects.get(user=request.session["cool_user"])
            notification.pending_received = 0
            notification.save()
        except Notification.DoesNotExist:
            notification = Notification(user=request.session["cool_user"])
            notification.save()
    except KeyError:
        pass
    user = User.objects.get(pk=request.session["cool_user"])
    if user.role.code == user.role.USER:
        received_requests = Request.objects.filter(lender=request.session["cool_user"], shared_from=Tool.HOME, lender_enabled=True).order_by('-id')
    elif user.role.code == user.role.ADMIN:
        received_requests = Request.objects.filter(lender=request.session["cool_user"], lender_enabled=True).order_by('-id')
    paginator = Paginator(received_requests, 10)
    page = request.GET.get('page')
    try:
        received_requests = paginator.page(page)
    except PageNotAnInteger:
        received_requests = paginator.page(1)
    except EmptyPage:
        received_requests = paginator.page(paginator.num_pages)

    context = {
        'received_requests': received_requests,
        'my_requests': True
    }
    return render(request, "request/received_requests.html", context)


@csrf_exempt
def action(request):
    if not is_user_logged_in(session=request.session):
        return JsonResponse({'status_code': 500, 'message': 'An error happened when approving or rejecting the request'})
    if 'is_shared_zone' not in request.session:
        return JsonResponse({'status_code': 500, 'message': 'An error happened when approving or rejecting the request'})

    if request.method == 'POST':
        try:
            received_request = Request.objects.get(pk=request.POST['request_id'])
            if request.POST['action'] == Request.APPROVED and received_request.tool.status == received_request.tool.BORROWED:
                return JsonResponse({'status_code': 500, 'message': 'You cannot approve this request. The tool is borrowed.'})
            received_request.status = request.POST['action']
            received_request.comment = request.POST['comment']
            message = ""
            optional = ""

            if request.POST['action'] == Request.REJECTED:
                message = "The borrowing request was rejected successfully!"
            elif request.POST['action'] == Request.APPROVED:
                received_request.tool.status = received_request.tool.BORROWED
                received_request.tool.save()
                message = "The borrowing request was approved successfully!"
                optional = "Please return the tool as soon as you finish using it. Remind the owner to mark the tool as returned."
            received_request.save()
            try:
                notification = Notification.objects.get(user=received_request.borrower)
            except Notification.DoesNotExist:
                notification = Notification(user=received_request.borrower)
                notification.save()
            notification.increment_sent()
            notification.save()
            try:
                send_email('request_action.txt', 'request_action.html', {'tool_name': received_request.tool.name, 'request_status': received_request.get_status_choices(), 'message': received_request.comment, 'optional': optional}, "Borrowing Request Information", received_request.borrower.email)
            except Exception as e:
                print(e)
            response = {'statusCode': 200, 'message': message, 'status': received_request.get_status_choices()}
        except Exception as e:
            print(e)
            response = {'status_code': 500, 'message': 'An error happened when approving or rejecting the request'}
        return JsonResponse(response)


def return_tool(request, pk):
    if not is_user_logged_in(session=request.session):
        return redirect(reverse('sign_in'))
    if 'is_shared_zone' not in request.session:
        return redirect(reverse('shared_zone:index'))
    if request.method == 'GET':
        try:
            received_request = Request.objects.get(pk=pk)
        except Request.DoesNotExist:
            messages.error(request, "No such request exists. Please verify information.")
            return redirect(reverse('request:received'))
        user = User.objects.get(pk=request.session["cool_user"])
        if received_request.status == Request.APPROVED and ((received_request.shared_from == Tool.HOME and received_request.lender == user) or (received_request.shared_from == Tool.SHED and User.objects.filter(pk=user.id, role__code=user.role.ADMIN).count() == 1)):
            received_request.tool.status = Tool.AVAILABLE
            received_request.tool.save()
            received_request.status = Request.RETURNED
            received_request.may_leave_comment = True
            received_request.returned_date = datetime.datetime.now()
            received_request.save()
            messages.success(request, "The tool was marked as returned successfully.")
        else:
            messages.error(request, "Conditions to return the tool were not met.")
    return redirect(reverse('request:received'))


def move_to_history(request, ac, pk):
    if not is_user_logged_in(session=request.session):
        return redirect(reverse('sign_in'))
    if 'is_shared_zone' not in request.session:
        return redirect(reverse('shared_zone:index'))
    if request.method == 'GET':
        try:
            borrowing_request = Request.objects.get(pk=pk)
        except Request.DoesNotExist:
            return HttpResponseForbidden()
        if ac == "sent" and borrowing_request.borrower.id == request.session["cool_user"]:
            borrowing_request.borrower_enabled = False
            borrowing_request.save()
            return redirect(reverse('request:sent'))
        elif ac == "received" and borrowing_request.lender.id == request.session["cool_user"]:
            borrowing_request.lender_enabled = False
            borrowing_request.save()
            return redirect(reverse('request:received'))
    return HttpResponseForbidden()
