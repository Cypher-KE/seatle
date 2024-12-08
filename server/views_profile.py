from django.shortcuts import render
from django.contrib.auth import authenticate

from server.forms import PasswordForm, ProfileForm, PropertyOwnerCreationForm
from server.models import Action, Account, Message, Property
from server import views
from server import logger
from server import message

def profile_view(request):
    # Authentication check
    authentication_result = views.authentication_check(request)
    if authentication_result is not None:
        return authentication_result
    # Get template data from session
    template_data = views.parse_session(request)
    # Proceed with rest of the view
    template_data['total_logins'] = Action.objects.filter(description__icontains="Account login").count()
    template_data['total_logouts'] = Action.objects.filter(description__icontains="Account logout").count()
    template_data['total_registered'] = Action.objects.filter(description__icontains="registered").count()
    message.parse_message_archive(request, template_data)
    template_data['messages'] = Message.objects.filter(target=request.user.account, target_deleted=False)
    total_properties = Property.objects.count()
    context = {
        'total_properties': total_properties
    }
    return render(request, 'house/profile.html', template_data)

def password_view(request):
    # Authentication check
    authentication_result = views.authentication_check(request)
    if authentication_result is not None: return authentication_result
    # Get template data from session
    template_data = views.parse_session(request,{'form_button':"Change password"})
    # Proceed with rest of the view
    if request.method == 'POST':
        form = PasswordForm(request.POST)
        if form.is_valid():
            user = authenticate(username=request.user.username, password=form.cleaned_data['password_current'])
            if user is None:
                form.mark_error('password_current','Incorrect Password')
            else:
                user = request.user
                user.set_password(form.cleaned_data['password_first'])
                user.save()
                logger.log(Action.ACTION_ACCOUNT,"Account password change",request.user.account)
                form = PasswordForm() # Clean the form when the page is redisplayed
                template_data['alert_success'] = "Your password has been changed"
    else:
        form = PasswordForm()
    template_data['form'] = form
    return render(request,'house/profile/password.html',template_data)


def update_view(request):
    # Authentication check.
    authentication_result = views.authentication_check(request)
    if authentication_result is not None: return authentication_result
    # Get the template data from the session
    template_data = views.parse_session(request, {'form_button': "Update profile"})
    # Proceed with the rest of the view
    profile = request.user.account.profile
    if request.method == 'POST':
        if request.user.account.role != Account.ACCOUNT_TENANT:
            form = ProfileForm(request.POST)
        else:
            form = ProfileForm(request.POST)
        if form.is_valid():
            form.assign(profile)
            profile.save()
            logger.log(Action.ACTION_ACCOUNT, "Account info updated", request.user.account)
            template_data['alert_success'] = "Your profile has been updated!"
    else:
        if request.user.account.role != Account.ACCOUNT_TENANT:
            form = ProfileForm(profile.get_populated_fields())
        else:
            form = ProfileForm(profile.get_populated_fields())
    template_data['form'] = form
    return render(request, 'house/profile/update.html', template_data)


def add_owner_details(request):
    form = PropertyOwnerCreationForm()
    form.profile = request.user.account.profile.pk

    if request.method == 'POST':
        owner_form = PropertyOwnerCreationForm(request.POST, request.FILES)

        print(owner_form.data)
        print(owner_form.files)
        if owner_form.is_valid():
            print("pass")
            owner = owner_form.save(commit=False)
            owner.profile = request.user.account.profile
            owner_form.save()
        else:
            print("fail")
            print(owner_form.errors)
    return render(request, 'house/profile/add_owner.html', {"form":form})


