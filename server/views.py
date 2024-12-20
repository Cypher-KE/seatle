from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
import datetime
from server.models import Account, Profile, Action
from server import logger
from server.utils import render_to_pdf
from django.views.generic import View
from django.template.loader import get_template
import socket
from .forms import PropertyCreationForm, FacilitiesForm,PropertyEditForm
from .models import Property, Facilities, PropertyOwner
from django.contrib.auth.decorators import login_required, user_passes_test
# Create your views here.
def authentication_check(request, required_roles=None, required_GET=None):
    """
    :param request: page request
    :param required_roles: role values of the users allowed to view the page
    :param required_GET:GET values that the page needs to function properly
    :return: A redirect request if there's a problem, None otherwise
    """
    # Authentication check. Users not logged in cannot view this page
    if not request.user.is_authenticated:
        request.session['alert_danger'] = "You must be logged into Becima to view that page."
        return HttpResponseRedirect('/')
    # Sanity Check. Users without accounts cannot interact with virtual clinic
    try:
        request.user.account
    except ObjectDoesNotExist:
        request.session['alert_danger'] = "Your account was not properly created, please try a different account."
        return HttpResponseRedirect('/logout/')
    # Permission check
    if required_roles and request.user.account.role not in required_roles:
        request.session['alert_danger'] = "You don't have permission to view that page."
        return HttpResponseRedirect('/error/denied/')
    # Validation check. Make sure this page has any required GET keys
    if required_GET:
        for key in required_GET:
            if key not in request.GET:
                request.session['alert_danger'] = "Looks like you tried to use a malformed URL"
                return HttpResponseRedirect('/error/denied/')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def parse_session(request, template_data=None):
    """
    Checks the session for any alert data. If there is alert data, it added to the given template data.
    :param request: The request to check session data for
    :param template_data: The dictionary to update
    :return: The updated dictionary
    """
    server_ip1 = socket.gethostbyname(socket.getfqdn())
    client_ip = get_client_ip(request)
    if template_data is None:
        template_data = {}
    if request.session.has_key('alert_success'):
        template_data['alert_success'] = request.session.get('alert_success')
        del request.session['alert_success']
    if request.session.has_key('alert_danger'):
        template_data['alert_danger'] = request.session.get('alert_danger')
        del request.session['alert_danger']

    template_data['server_ip1'] = server_ip1
    template_data['client_ip'] = client_ip
    return template_data


def register_user(email, password, firstname, lastname, role):
    user = User.objects.create_user(
        email.lower(),
        email.lower(),
        password
    )
    profile = Profile(
        firstname=firstname,
        lastname=lastname
    )
    profile.save()
    account = Account(
        role=role,
        profile=profile,
        user=user
    )
    account.save()
    logger.log(Action.ACTION_ACCOUNT,"Account registered",account)
    return user


def sanitize_js(string):
    return string.replace("\\","\\\\").replace("'","\\'")


def is_property_owner(request):
    user = request.user 
    try:
        owner = PropertyOwner.objects.get(email = user.email)
    except PropertyOwner.DoesNotExist:
        return False

    return True
