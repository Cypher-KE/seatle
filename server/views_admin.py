from csv import QUOTE_MINIMAL, writer
import re
import sqlite3
import sys
from django.core.management import call_command
from django.core import serializers
from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.db.utils import IntegrityError
from server.forms import EmployeeRegistrationForm, ImportForm, ExportForm, StatisticsForm
from server.models import Account, Action, Statistics,  Profile, Message
from server import logger
from server import views

def user_archive(request):
    # Authentication check.
    authentication_result = views.authentication_check(request, [Account.ACCOUNT_ADMIN])
    if authentication_result is not None:
        return authentication_result
    # Get the template data from the session
    template_data = views.parse_session(request)
    # Proceed with the rest of the view
    if request.method == 'POST':
        if 'delete' in request.POST and 'pk' in request.POST:
            pk = request.POST['pk']
            try:
                user = Account.objects.get(pk=pk)
            except Exception:
                template_data['alert_danger'] = "Unable to delete the user. Please try again later"
                return
            user.archive = True
            user.save()
            #logger.log(Action.ACTION_ADMIN, 'Admin deleted a user',user)
            template_data['alert_success'] = "The user has been deleted."
            return HttpResponseRedirect('/admin/users')


def view_archived_users(request):
    # Authentication check.
    authentication_result = views.authentication_check(request, [Account.ACCOUNT_ADMIN])
    if authentication_result is not None:
        return authentication_result
    # Get the template data from the session
    template_data = views.parse_session(request)
    # Proceed with the rest of the view
    template_data['query'] = Account.objects.filter(archive=True)
    return render(request, 'house/admin/archived_users.html', template_data)


def restore_user(request):
    # Authentication check.
    authentication_result = views.authentication_check(request, [Account.ACCOUNT_ADMIN])
    if authentication_result is not None:
        return authentication_result
    # Get the template data from the session
    template_data = views.parse_session(request)
    # Proceed with the rest of the view
    if request.method == 'POST':
        if 'restore' in request.POST and 'pk' in request.POST:
            pk = request.POST['pk']
            try:
                user = Account.objects.get(pk=pk)
            except Exception:
                template_data['alert_danger'] = "Unable to delete the user. Please try again later"
                return HttpResponseRedirect('/admin/users')
            user.archive = False
            user.save()
            logger.log(Action.ACTION_ADMIN, 'Admin restored the user',user)
            template_data['alert_success'] = "The user has been restored."
            return HttpResponseRedirect('/admin/users')
    return HttpResponseRedirect('/admin/users')


def users_view(request):
    # Authentication check.
    authentication_result = views.authentication_check(request, [Account.ACCOUNT_ADMIN])
    if authentication_result is not None:
        return authentication_result
    # Get the template data from the session
    template_data = views.parse_session(request)
    # Proceed with the rest of the view
    if request.method == 'POST':
        pk = request.POST['pk']
        role = request.POST['role']
        account = Account.objects.get(pk=pk)
        if account is not None:
            account.role = role
            account.save()
            logger.log(Action.ACTION_ADMIN, 'Admin modified ' + account.user.username + "'s role", request.user.account)
            template_data['alert_success'] = "Updated" + account.user.username + "'s role!"
    # Parse search sorting
    template_data['query'] = Account.objects.filter(archive=False).order_by('-role')
    return render(request,'house/admin/users.html', template_data)


def activity_view(request):
    # Authentication check.
    authentication_result = views.authentication_check(request, [Account.ACCOUNT_ADMIN])
    if authentication_result is not None: return authentication_result
    # Get the template data from the session
    template_data = views.parse_session(request)
    # Proceed with the rest of the view
    # Parse search sorting
    template_data['query'] = Action.objects.all().order_by('-timePerformed')
    return render(request,'house/admin/activity.html',template_data)

def createemployee_view(request):
    # Authentication check.
    authentication_result = views.authentication_check(request, [Account.ACCOUNT_ADMIN])
    if authentication_result is not None: return authentication_result
    # Get the template data from the session
    template_data = views.parse_session(request,{'form_button':"Register"})
    # Proceed with the rest of the view
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            user = views.register_user(
                form.cleaned_data['email'],
                form.cleaned_data['password_first'],
                form.cleaned_data['firstname'],
                form.cleaned_data['lastname'],
                form.cleaned_data['employee']
            )
            logger.log(Action.ACTION_ADMIN, 'Admin registered '+ user.username, request.user.account)
            request.session['alert_success'] = "Successfully created new employee account"
            return HttpResponseRedirect('/admin/users/')
    else:
        form = EmployeeRegistrationForm()
    template_data['form'] = form
    return render(request,'house/admin/createemployee.html', template_data)


def statistic_view(request):
    # Authentication check.
    authentication_result = views.authentication_check(request, [Account.ACCOUNT_ADMIN])
    if authentication_result is not None: return authentication_result
    # Get the template data from the session
    template_data = views.parse_session(request, {'form_button': "Get Statistics"})
    # Proceed with the rest of the view
    default = {}
    request.POST._mutable = True
    request.POST.update(default)
    predate_filter = Action.objects.all()
    template_data['pre_filter'] = predate_filter.count()
    form = StatisticsForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            statistics = Statistics(
                startDate = form.cleaned_data['startDate'],
                endDate = form.cleaned_data['endDate'],
            )
            date_filter = Action.objects.all().filter(timePerformed__range = (statistics.startDate,statistics.endDate))
            template_data['temp'] = date_filter.count()
            template_data['start'] = statistics.startDate
            template_data['end'] = statistics.endDate

            template_data['total_logins'] = Action.objects.filter(description__icontains="Account login",timePerformed__range = (statistics.startDate, statistics.endDate) ).count()
            template_data['total_logouts'] = Action.objects.filter(description__icontains="Account logout",timePerformed__range = (statistics.startDate, statistics.endDate)).count()
            template_data['total_registered'] = Action.objects.filter(description__icontains="registered",timePerformed__range = (statistics.startDate, statistics.endDate)).count()

    else:
        form._errors = {}
        statistics = Statistics(
                startDate = 0,
                endDate = 0,
            )
        errdate_filter = Action.objects.all()
        template_data['errdate_filter'] = errdate_filter.count()
        template_data['start'] = statistics.startDate
        template_data['end'] = statistics.endDate

        template_data['total_logins'] = 0
        template_data['total_logouts'] = 0
        template_data['total_registered'] = 0
    template_data['form'] =form

    return render(request,'house/admin/statistics.html', template_data)


def csv_import_view(request):
    # Authentication check.
    authentication_result = views.authentication_check(request, [Account.ACCOUNT_ADMIN])
    if authentication_result is not None: return authentication_result
    template_data = views.parse_session(request, {'form_button': "Submit"})
    if request.method=='POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['upload']
            for line in file:
                first_word = re.split('[,]',line.decode("utf-8").strip())[0].lower()
                if first_word == 'firstname':
                    count = handle_user_csv(file)
                    m = str(count[0])+' users are successfully uploaded, '+str(count[1])+' duplicate accounts.'
                    if count[0] == 0:
                        template_data['alert_danger'] = m
                    else:
                        template_data['alert_success'] = m
                elif first_word=='name':
                    count = handle_hospital_csv(file)
                    m = str(count[0])+' hospitals are successfully uploaded, '+str(count[1])+' duplicate hospitals.'
                    if count[0] == 0:
                        template_data['alert_danger'] = m
                    else:
                        template_data['alert_success'] = m
                else:
                    template_data['alert_danger'] = "Invalid CSV format."
                template_data['form'] = form
                return render(request,'house/admin/import.html', template_data)
        else:
            template_data['alert_danger'] = "Please choose a file to upload"
    form = ImportForm()
    template_data['form'] = form
    return render(request,'house/admin/import.html',template_data)


def handle_user_csv(f):
    """
    Handles a CSV containing User information.
    The first row should contain the following information
        FirstName,LastName,Account,Username,Email,Hospital
    with the following lines containing information about zero or more Users.
    :param f: The file object containing the CSV
    :return: The # of successes and failures
    """
    success = 0
    fail = 0
    is_first = True
    for row in f:
        if is_first:
            is_first=False
            continue    # breaks out of for loop
        line = re.split('[,]',row.decode("utf-8").strip())
        if line[0]:
            f_name = line[0]
            l_name = line[1]
            role = line[2].lower()
            username = line[3].lower()
            try:
                if role== "owner":
                    views.register_user(
                        username,'password',f_name,l_name,
                        Account.ACCOUNT_OWNER,
                    )
                elif role == "admin":
                    views.register_user(
                        username, 'password', f_name, l_name,
                        Account.ACCOUNT_ADMIN,
                    )
                else:
                    views.register_user(
                        username, 'password', f_name, l_name,
                        Account.ACCOUNT_TENANT,
                    )
                success+=1
            except (IntegrityError, ValueError):
                fail+=1
                continue
    return success,fail

def csv_export_view(request):
    # Authentication check
    authentication_result = views.authentication_check(request,[Account.ACCOUNT_ADMIN])
    if authentication_result is not None:
        return authentication_result
    template_data = views.parse_session(request,{'form_button':"Submit"})
    if request.method == 'POST':
        if request.POST['export'] == 'users':
            return generate_user_csv()
        else:
            template_data['alert_danger'] = 'Please choose a file to download'
    template_data['form'] = ExportForm()
    return render(request,'house/admin/export.html', template_data)


def generate_user_csv():
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'
    write = writer(response, delimiter=',', quotechar='"', quoting=QUOTE_MINIMAL)
    write.writerow(['FirstName', 'LastName', 'Role', 'Username'])
    for a in Account.objects.all():
        firstname = a.profile.firstname
        lastname = a.profile.lastname
        role = a.role
        username = a.user.username
        if role== 10:
            role = 'Tenant'
        elif role == 20:
            role='Owner'
        elif role== 30:
            role='Admin'
        else:
            role='Unknown'
        write.writerow([firstname,lastname,role,username])
    return response



