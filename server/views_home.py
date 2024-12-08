from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout

from server.forms import LoginForm, AccountRegisterForm
from server.models import Account, Action
from server import views
from server import logger


def setup_view(request):
    if Account.objects.all().count() > 0:
        request.session['alert_success'] = "Setup has already been completed."
        return HttpResponseRedirect('/')
    # Get template data from the session
    template_data = views.parse_session(request,{'form_button':"Register"})
    # Proceed with rest of the view
    if request.method == 'POST':
        form = AccountRegisterForm(request.POST)
        if form.is_valid():
            views.register_user(
                form.cleaned_data['email'],
                form.cleaned_data['password_first'],
                form.cleaned_data['firstname'],
                form.cleaned_data['lastname'],
                Account.ACCOUNT_ADMIN
            )
            user = authenticate(
                username=form.cleaned_data['email'].lower(),  # Make sure it's lowercase
                password=form.cleaned_data['password_first']
            )
            logger.log(Action.ACTION_ACCOUNT, "Account login", user.account)
            login(request, user)
            request.session['alert_success'] = "Successfully setup Becima's primary admin account."
            return HttpResponseRedirect('/profile/')
    else:
        form = AccountRegisterForm()
    template_data['form'] = form
    return render(request,'house/setup.html',template_data)


from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.contrib import messages
from server.models import Action

def logout_view(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'account'):
            account = request.user.account
            logger.log(Action.ACTION_ACCOUNT, "Account logout", account)
    # Django deletes the session on logout, so we need to preserve any alerts currently waiting to be displayed
    saved_data = {}
    if 'alert_success' in request.session:
        saved_data['alert_success'] = request.session.pop('alert_success')
    else:
        saved_data['alert_success'] = "You have successfully logged out."
    if 'alert_danger' in request.session:
        saved_data['alert_danger'] = request.session.pop('alert_danger')
    logout(request)
    if 'alert_success' in saved_data:
        request.session['alert_success'] = saved_data['alert_success']
    if 'alert_danger' in saved_data:
        request.session['alert_danger'] = saved_data['alert_danger']
    return HttpResponseRedirect('/')



def login_view(request):
    # Authentication check. Users currently logged in cannot view this page.
    if request.user.is_authenticated:
        return HttpResponseRedirect('/profile/')
    elif Account.objects.all().count() == 0:
        return HttpResponseRedirect('/setup/')
    # get template data from session
    template_data = views.parse_session(request,{'form_button':"Login"})
    # Proceed with the rest of view
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username = form.cleaned_data['email'].lower(),
                password = form.cleaned_data['password']
            )
            userInfo = Account.objects.get(user=user)
            if userInfo.archive == False:
                login(request,user)
                logger.log(Action.ACTION_ACCOUNT,"Account login",request.user.account)
                request.session['alert_success'] = "Successfully logged into template."
                return HttpResponseRedirect('/profile/')
            else:
                request.session['alert_danger'] = "Account is archived! Please create a new account"
                return HttpResponseRedirect('/register/')
    else:
        form = LoginForm()
    template_data['form'] = form
    return render(request, 'house/login.html', template_data)


def register_view(request):
    # Authentication check. Users logged in cannot view this page.
    if request.user.is_authenticated:
        return HttpResponseRedirect('/profile/')
    elif Account.objects.all().count() == 0:
        return HttpResponseRedirect('/setup/')
    # Get template data from session
    template_data = views.parse_session(request, {'form_button': "Register"})
    # Proceed with rest of the view
    if request.method == 'POST':
        form = AccountRegisterForm(request.POST)
        if form.is_valid():
            views.register_user(
                form.cleaned_data['email'],
                form.cleaned_data['password_first'],
                form.cleaned_data['firstname'],
                form.cleaned_data['lastname'],
                Account.ACCOUNT_TENANT
            )
            user = authenticate(
                username = form.cleaned_data['email'].lower(),
                password = form.cleaned_data['password_first']
            )
            logger.log(Action.ACTION_ACCOUNT, "Account Login", user.account)
            login(request,user)
            request.session['alert_success'] = "Successfully registered with template."
            return HttpResponseRedirect('/profile/')
    else:
        form = AccountRegisterForm()
    template_data['form'] = form
    return render(request,'house/register.html',template_data)

def error_denied_view(request):
    # Authentication check
    authentication_result = views.authentication_check(request)
    if authentication_result is not None:
        return authentication_result
    # Get template data from session
    template_data = views.parse_session(request)
    # Proceed with rest of the view
    return render(request,'house/error/denied.html',template_data)
