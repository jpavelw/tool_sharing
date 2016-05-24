from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.core import serializers
from manage_tools.models import Tool, ToolReview
from user.models import User
from .forms import ToolForm
from utils.utilities import is_user_logged_in
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from request.models import Request


def my_tools(request):
    if not is_user_logged_in(session=request.session):
        return redirect(reverse('sign_in'))
    if 'is_shared_zone' not in request.session:
        return redirect(reverse('shared_zone:index'))
    title = "My Tools"
    tool_list = Tool.objects.filter(owner=request.session["cool_user"], enabled=1).order_by('-id')
    
    paginator = Paginator(tool_list, 10)
    page = request.GET.get('page')

    try:
        tools = paginator.page(page)
    except PageNotAnInteger:
        tools = paginator.page(1)
    except EmptyPage:
        tools = paginator.page(paginator.num_pages)
    context = {
        "title": title,
        "tools": tools,
        'my_tools': True
    }
    return render(request, "tool_management/my_tools.html", context)


def new_tool(request):
    if not is_user_logged_in(session=request.session):
        return redirect(reverse('sign_in'))
    if 'is_shared_zone' not in request.session:
        return redirect(reverse('shared_zone:index'))
    form = ToolForm(request.POST or None, request.FILES or None)
    success = None
    msg = None

    if form.is_valid():
        user = User.objects.get(id=request.session["cool_user"], enabled=1)
        form.set_owner(user)
        form.generate_code()
        form.save()
        return redirect(reverse('manage_tools:my_tools'))
    context = {
        "title": "New Tool",
        "form": form,
        "bottom_title": "Save",
        "update": False,
        'my_tools': True,
        "success": success,
        "msg": msg
    }
    return render(request, "tool_management/details_tool.html", context)


def edit_tool(request, pk):
    if not is_user_logged_in(session=request.session):
        return redirect(reverse('sign_in'))
    if 'is_shared_zone' not in request.session:
        return redirect(reverse('shared_zone:index'))
    if request.method == 'GET':
        try:
            tool = Tool.objects.get(pk=pk, owner=request.session["cool_user"])
            if tool.status == Tool.BORROWED:
                context = {
                    "not_found": 'You cannot edit a borrowed tool',
                    'my_tools': True
                }
            else:
                form = ToolForm(instance=tool)
                context = {
                    "title": "Edit Tool",
                    "form": form,
                    "bottom_title": "Update",
                    "update": True,
                    "pk": pk,
                    'my_tools': True,
                    "img": tool.picture.url
                }
        except Tool.DoesNotExist:
            context = {
                "not_found": 'The item you requested does not exist',
                'my_tools': True
            }
    if request.method == 'POST':
        try:
            tool = Tool.objects.get(pk=request.POST['id'], enabled=1)
            form = ToolForm(request.POST or None, request.FILES or None, instance=tool)
            if form.is_valid():
                form.save()
                return redirect(reverse('manage_tools:my_tools'))
            context = {
                "title": "Edit Tool",
                "form": form,
                "bottom_title": "Update",
                "update": True,
                "pk": pk,
                'my_tools': True,
                "img": tool.picture.url
            }
        except Tool.DoesNotExist:
            context = {
                "not_found": 'The item you requested does not exist',
                'my_tools': True
            }
    return render(request, "tool_management/details_tool.html", context)


def get_reviews(request, pk):
    if not is_user_logged_in(session=request.session):
        return JsonResponse({'status_code': 500, 'message': 'An error happened when getting the reviews'})
    if 'is_shared_zone' not in request.session:
        return JsonResponse({'status_code': 500, 'message': 'An error happened when getting the reviews'})
    try:
        reviews = ToolReview.objects.filter(tool_id=pk).order_by('-timestamp')
        data = serializers.serialize("json", reviews)
        response = {'statusCode': 200, 'message': 'OK', 'data': data}
    except:
        response = {'status_code': 500, 'message': 'An error happened when getting the reviews'}
    return JsonResponse(response)


def post_review(request, pk):
    if not is_user_logged_in(session=request.session):
        return JsonResponse({'status_code': 500, 'message': 'An error happened when posting the reviews'})
    if 'is_shared_zone' not in request.session:
        return JsonResponse({'status_code': 500, 'message': 'An error happened when posting the reviews'})
    try:
        review = ToolReview()
        review.rate = request.POST['rate']
        review.title = request.POST['title']
        review.description = request.POST['description']
        review.user_name = request.POST['user_name']
        user = User.objects.get(pk=request.session["cool_user"])
        tool = Tool.objects.get(pk=pk)
        review.user = user
        review.tool = tool
        review.save()
        the_requests = Request.objects.filter(borrower=request.session["cool_user"], tool=pk, status=Request.RETURNED, may_leave_comment=True).order_by('-tool')
        for the_request in the_requests:
            the_request.may_leave_comment = False
            the_request.save()
        data = serializers.serialize("json", [review])
        response = {'statusCode': 200, 'message': 'OK', 'data': data}
    except:
        response = {'status_code': 500, 'message': 'An error happened when posting the reviews'}
    return JsonResponse(response)


def remove_tool(request, pk):
    if not is_user_logged_in(session=request.session):
        return redirect(reverse('sign_in'))
    if 'is_shared_zone' not in request.session:
        return redirect(reverse('shared_zone:index'))
    if request.method == 'GET':
        try:
            tool = Tool.objects.get(pk=pk, owner=request.session["cool_user"])
            tool.enabled = False
            tool.save()
        except Tool.DoesNotExist:
            pass
        return redirect(reverse('manage_tools:my_tools'))


@csrf_exempt
def update_status(request, pk):
    if not is_user_logged_in(session=request.session):
        return JsonResponse({'status_code': 500, 'message': 'An error happened when updating the tool'})
    if 'is_shared_zone' not in request.session:
        return JsonResponse({'status_code': 500, 'message': 'An error happened when updating the tool'})
    try:
        tool = Tool.objects.get(pk=pk, owner=request.session["cool_user"])
        tool.status = request.POST['status_code']
        tool.save()
        response = {'statusCode': 200, 'message': 'OK'}
    except:
        response = {'status_code': 500, 'message': 'An error happened when updating the tool'}
    return JsonResponse(response)


def available_reviews(request):
    if not is_user_logged_in(session=request.session):
        return redirect(reverse('sign_in'))
    if 'is_shared_zone' not in request.session:
        return redirect(reverse('shared_zone:index'))
    if request.method == 'GET':
        context = {'borrow': True}
        try:
            requests = Request.objects.filter(borrower=request.session["cool_user"], status=Request.RETURNED, may_leave_comment=True).order_by('-tool')
            if requests.count() > 0:
                paginator = Paginator(requests, 10)
                page = request.GET.get('page')
                try:
                    requests = paginator.page(page)
                except PageNotAnInteger:
                    requests = paginator.page(1)
                except EmptyPage:
                    requests = paginator.page(paginator.num_pages)
                context['requests'] = requests
        except Request.DoesNotExist:
            pass
        return render(request, "tool_management/available_reviews.html", context)


def review_review(request, pk):
    requests = Request.objects.filter(borrower=request.session["cool_user"], tool=pk, status=Request.RETURNED, may_leave_comment=True)
    for request_one in requests:
        request_one.may_leave_comment = False
        request_one.save()
    return redirect(reverse('tool_listing:tool_detail', args=[pk]))
