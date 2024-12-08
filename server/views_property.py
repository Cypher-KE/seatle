from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from .decorators import account_role_required
from .forms import PropertyCreationForm, FacilitiesForm, UnitCreationForm, PropertyEditForm, PublicUtilsForm, \
    BookingForm, PaymentForm, PhotoForm
from .models import Property, Unit, Profile, Floor, Account, Booking, Photo


# TODO: Finish UTILS
# Create your views here.

def list_properties(request):
    properties = Property.objects.all()
    print(properties)

    return render(request, 'listings/index.html', {'properties': properties})


def get_property(request, pk):
    print(pk)
    try:
        property_one = Property.objects.get(id=pk)
        owner = property_one.owner
        profile = owner.profile
        print(f"profile:-> {profile.firstname} {profile.lastname}")
        print(profile.id)

        # print(request.user){'property': property_one, 'owner': owner}
        context = {'property': property_one, 'owner': owner}
        try:
            facilities = property_one.facilities
            context['facilities'] = facilities
        except:
            print("no facilities")

        try:
            utils = property_one.public_utilities
            context['utils'] = utils
        except:
            print("no facilities")

        try:
            count = property_one.units.all().count()
            context["count"] = count
        except:
            print("no facilities")

        try:
            photo_count = property_one.photos.all().count()
            context["photo_range"] = range(1, photo_count)
        except:
            print("no photos")
        # return render(request, 'property/index.html',
        #               {'property': property_one, 'facilities': facilities, 'owner': owner})
        return render(request, 'property/index.html', context)
    except Property.DoesNotExist:
        return None


@account_role_required(Account.ACCOUNT_OWNER)
def new_property(request):
    form = PropertyCreationForm()
    user = request.user
    print(user.account.role)
    if request.method == 'POST':
        form = PropertyCreationForm(request.POST)
        if form.is_valid():
            print("pass\n")
            print(form.cleaned_data)

            new_prop = form.save(commit=False)
            owner = user.account.profile.owner
            owner.number_of_properties += 1
            new_prop.owner = owner
            print(new_prop)
            new_prop.save()
            owner.save()

            no_of_floors = form.cleaned_data["number_of_floors"]
            for i in range(0, no_of_floors):
                Floor.objects.create(
                    property=new_prop,
                    number=i
                )
            return redirect("server:owner_listings")
        else:
            print('problem')
            print(form.errors)
            print(form.cleaned_data)

    return render(request, 'new_property/index.html', {'form': form})


#@list_properties
@account_role_required(Account.ACCOUNT_OWNER, Account.ACCOUNT_ADMIN)
def property_facilities(request, pk):
    prop = Property.objects.get(id=pk)
    print("posted")
    if request.method == 'POST':
        form = FacilitiesForm(request.POST)

        try:
            facilities = prop.facilities
            form = FacilitiesForm(request.POST, instance=facilities)
            print(facilities)
        except:
            print("no facilities")
        if form.is_valid():
            print("pass\n")
            form_data = form.cleaned_data
            new_property_facilities = form.save()
            print(new_property_facilities)
            return redirect('server:property', pk=pk)
        else:
            print('problem')
            print(form.errors)
            print(form.cleaned_data)

            return redirect('server:property', pk=pk)


@account_role_required(Account.ACCOUNT_OWNER, Account.ACCOUNT_ADMIN)
def property_utils(request, pk):
    print("utils")
    prop = Property.objects.get(id=pk)
    if request.method == "POST":
        form = PublicUtilsForm(request.POST)

        try:
            utils = prop.public_utilities
            form = PublicUtilsForm(request.POST, instance=utils)
            print(utils)
        except:
            print("no facilities")

        if form.is_valid():
            print("pass\n")
            print(form.cleaned_data)
            utils = form.save()
            print(utils)
            return redirect('server:property', pk=pk)
        else:
            print('problem')
            print(form.errors)
            print(form.cleaned_data)

            return redirect('server:property', pk=pk)


@account_role_required(Account.ACCOUNT_OWNER, Account.ACCOUNT_ADMIN)
def edit_property(request, pk):
    updated_property = Property.objects.get(id=pk)
    form = PropertyEditForm(instance=updated_property)

    facilities_form = FacilitiesForm(initial={'property': updated_property})
    utils_form = PublicUtilsForm(initial={'prop': updated_property})
    try:
        facilities = updated_property.facilities
        facilities_form = FacilitiesForm(instance=facilities)
        print(facilities)
    except:
        print("no facilities")

    try:
        utils = updated_property.public_utilities
        utils_form = PublicUtilsForm(instance=utils)
        print(utils)
    except:
        print("no facilities")

    if request.method == 'POST':
        form = PropertyEditForm(request.POST, instance=updated_property)
        if form.is_valid():
            print("pass\n")
            updated_property = form.save()
            print(updated_property)
            return redirect('server:property', pk=pk)
        else:
            print("fail")
            print(form.errors)
    return render(request, 'edit/index.html',
                  {'form': form, 'facilities_form': facilities_form, 'property': updated_property,
                   'utils_form': utils_form})

def upload_photos(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    form = PhotoForm()

    if request.method == 'POST':
        images = request.FILES.getlist('image')

        for image in images:
            Photo.objects.create(property=prop, image=image)

        return redirect('server:property', pk=prop.id)

    return render(request, 'photos/prop_photos.html', {'property': prop, 'form': form})


def advance_payment(request, pk):
    property_one = Property.objects.get(id=pk)
    return render(request, 'advance_payment_page/index.html', {'property': property_one})


# Unit views
@account_role_required(Account.ACCOUNT_OWNER)
def new_unit(request, pk):
    selected_property = Property.objects.get(pk=pk)
    print(selected_property.floors.all().count())

    form = UnitCreationForm(initial={'unit_price': selected_property.price}, property_id=pk)
    form.data["property"] = property
    if request.method == 'POST':
        form = UnitCreationForm(request.POST, property_id=pk)

        if form.is_valid():
            print("pass\n")
            print(form.cleaned_data)
            unit = form.save(commit=False)
            unit.property = selected_property
            print('saving')
            print(unit)
            unit.save()
            return redirect('server:listings')
        else:
            print('problem')
            print(form.errors)
            print(form.cleaned_data)

            return redirect('server:listings')
    return render(request, 'property/new_unit.html', {'property': selected_property, "form": form})


def get_units(request, pk):
    prop = Property.objects.get(id=pk)
    units = prop.units.all()
    return render(request, 'property/units.html', {'property': prop, 'units': units})


def get_unit(request, pk):
    unit = Unit.objects.get(pk=pk)
    form = BookingForm()
    context = {'unit': unit, 'form': form, 'flag': 'b'}

    if hasattr(request.user.account.profile, 'owner'):
        if unit.property.owner == request.user.account.profile.owner:
            context['bookings'] = unit.bookings.all()
            context['flag'] = 'o'

    return render(request, 'property/unit.html',context)


def owner_properties(request):
    owner = request.user.account.profile.owner
    properties = owner.properties.all()
    return render(request, 'listings/index.html', {'properties': properties})

def property_detail(request, pk):
    property = get_object_or_404(Property, id=pk)
    return render(request, 'property_detail.html', {'property': property})


def booking(request, pk):
    # booking
    # tenant = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="interested_account")
    # unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="unit")
    # level = models.CharField(max_length=20, choices=LEVEL, default=VIEWING)
    # next_date = models.DateTimeField(null=True)
    tenant = request.user.account
    print(tenant)

    payment_form = PaymentForm()
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            new_booking = form.save(commit=False)
            new_booking.tenant = tenant
            unit = Unit.objects.get(id=pk)
            new_booking.unit = unit
            new_booking = form.save(commit=True)
            payment_form = PaymentForm(
                initial={'booking': new_booking, 'property_unit': unit, 'made_by': request.user.account})
            print(new_booking)
            return render(request, 'property/unit.html', {'unit': unit, 'form': payment_form, 'flag': 'p'})
        else:
            return HttpResponse('<h1 style = "color:red"> ERROR CREATING FORM </h1>')
    else:
        one_booking = Booking.objects.get(id=pk)
        unit = one_booking.unit
        if unit.property.owner == request.user.account.profile.owner:
            return render(request, 'booking/b_detail.html',
                          {'booking': one_booking, 'flag': 'o'})  #flag identifies who is the user
        elif one_booking.tenant == request.user.account:
            return render(request, 'booking/b_detail.html', {'booking': one_booking, 'flag': 't'})
        else:
            return HttpResponse("<h1>Unauthorized</h1>")


def get_bookings(request):
    bookings = request.user.account.bookings.all()
    print(request.user.account.id)

    print(bookings)
    for b in bookings:
        print(b.unit.unitCode)
        if hasattr(b, 'payment'):
            print(b.payment.amount)
    return render(request, 'booking/index.html', {'bookings': bookings})


def get_booking_form(request, pk):
    booking = Booking.objects.get(id=pk)
    unit = booking.unit
    print(unit)
    payment_form = PaymentForm(initial={'booking': booking, 'property_unit': unit, 'made_by': request.user.account})
    return render(request, 'property/unit.html', {'unit': unit, 'form': payment_form, 'flag': 'p'})


@account_role_required(Account.ACCOUNT_OWNER)
def get_unit_bookings(request, pk):
    unit = Unit.objects.get(id=pk)
    if unit.property.owner == request.user.account.profile.owner:
        bookings = unit.bookings.all()
        return render(request, 'booking/index.html', {'bookings': bookings})
    else:
        return HttpResponse("<h1>Unauthorized</h1>")


def get_booking(request, pk):
    one_booking = Booking.objects.get(id=pk)
    unit = one_booking.unit
    if unit.property.owner == request.user.account.profile.owner:
        return render(request, 'booking/b_detail.html',
                      {'booking': one_booking, 'flag': 'o'})  #flag identifies who is the user
    elif one_booking.tenant == request.user.account:
        return render(request, 'booking/b_detail.html', {'booking': one_booking, 'flag': 't'})
    else:
        return HttpResponse("<h1>Unauthorized</h1>")


def delete_all_properties_test(request):
    Property.objects.all().delete()
    return HttpResponse("<h1>Deleted</h1>")
