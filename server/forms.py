from datetime import date

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.forms import ModelForm, DateTimeInput

from .models import Account, Profile, Message, Booking, PaymentDb, Photo, Floor
from .models import Property, Facilities, PublicUtils, Unit, PropertyOwner


def validate_username_available(username):
    """ validator that throws an error if the given username already exists."""

    if User.objects.filter(username__icontains=username).count():
        raise forms.ValidationError("This email is already registered")


def validate_username_exists(username):
    """ validator that throws an error if the given username doesn't exists."""

    if not User.objects.filter(username__icontains=username).count():
        raise forms.ValidationError("This email does not exist")


def validate_birthday(birthday):
    """ validator to check if date is realistic """
    if birthday.year < (date.today().year - 200):
        raise forms.ValidationError("Please choose a later date")
    elif birthday > date.today():
        raise forms.ValidationError("Please choose an earlier date")


def setup_field(field, placeholder=None):
    """
    This configures the given field to play nice with the bootstrap theme. Additionally, you can add
    an additional argument to set a placeholder text on the field.
    """
    field.widget.attrs['class'] = 'form-control'
    if placeholder is not None:
        field.widget.attrs['placeholder'] = placeholder


class BasicForm(forms.Form):
    def disable_field(self, field):
        """
        marks field as disabled
        :param field: name of the field
        """
        self.fields[field].widget.attrs['disabled'] = ""

    def mark_error(self, field, description):
        """
        Marks the given field as errous. The given description is displayed when the form it generated
        :param field: name of the field
        :param description: The error description
        """
        self._errors[field] = self.error_class([description])
        del self.cleaned_data[field]

    def clear_errors(self):
        self._errors = {}


class LoginForm(BasicForm):
    email = forms.EmailField(max_length=50, validators=[validate_username_exists])
    setup_field(email, 'Enter Email here')
    password = forms.CharField(max_length=50, widget=forms.PasswordInput())
    setup_field(password, 'Enter password here')

    def clean(self):
        """
        This is to make sure the password is valid for the given email.
        """
        cleaned_data = super(LoginForm, self).clean()
        username = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                self.mark_error('password', 'Incorrect password')
        return cleaned_data


class AccountRegisterForm(BasicForm):
    firstname = forms.CharField(label='First Name', max_length=50)
    setup_field(firstname, 'Enter first name here')
    lastname = forms.CharField(label='Last Name', max_length=50)
    setup_field(lastname, 'Enter last name here')
    email = forms.EmailField(max_length=50, validators=[validate_username_available])
    setup_field(email, 'Enter email here')
    password_first = forms.CharField(label='Password', min_length=1, max_length=50, widget=forms.PasswordInput())
    setup_field(password_first, "Enter password here")
    password_second = forms.CharField(label='', min_length=1, max_length=50, widget=forms.PasswordInput())
    setup_field(password_second, "Enter password again")

    def clean(self):
        """This is to make sure both passwords fields have the same values in them. If they don't mark
        them as erroneous."""
        cleaned_data = super(AccountRegisterForm, self).clean()
        password_first = cleaned_data.get('password_first')
        password_second = cleaned_data.get('password_second')
        if password_first and password_second and password_first != password_second:
            self.mark_error('password_second', 'Passwords do not match')
        return cleaned_data


class PasswordForm(BasicForm):
    password_current = forms.CharField(label='Current', max_length=50, widget=forms.PasswordInput())
    setup_field(password_current, 'Enter your current password here')
    password_first = forms.CharField(label='New', max_length=50, widget=forms.PasswordInput())
    setup_field(password_first, "Enter new password here")
    password_second = forms.CharField(label='', max_length=50, widget=forms.PasswordInput())
    setup_field(password_second, "Enter new password again")

    def clean(self):
        """
        This is to make sure both passwords fields have the same values in them. If they don't, mark
        them as erroneous. Also check if the current and new passwords are they same. If they are, then
        mark them as erroneous (we want different passwords).
        """
        cleaned_data = super(PasswordForm, self).clean()
        password_current = cleaned_data.get('password_current')
        password_first = cleaned_data.get('password_first')
        password_second = cleaned_data.get('password_second')
        if password_second and password_first:
            if password_second != password_first:
                self.mark_error('password_second', 'Passwords do not match')
            if password_current and password_current == password_first:
                self.mark_error('password_current', 'Your current and new passwords must be different')
        return cleaned_data


class ProfileForm(BasicForm):
    firstname = forms.CharField(label='First Name', max_length=50)
    setup_field(firstname, 'Enter first name here')
    lastname = forms.CharField(label='Last Name', max_length=50)
    setup_field(lastname, 'Enter last name here')
    sex = forms.ChoiceField(required=False, choices=Profile.GENDER)
    setup_field(sex)
    birthday = forms.DateField(required=False, validators=[validate_birthday])
    setup_field(birthday, 'Enter birthday as YYYY-MM-DD')
    phone = forms.CharField(required=False, max_length=10)
    setup_field(phone, 'Enter phone number here')

    def assign(self, profile):
        profile.firstname = self.cleaned_data['firstname']
        profile.lastname = self.cleaned_data['lastname']
        profile.sex = self.cleaned_data['sex']
        if self.cleaned_data['birthday'] is not None:
            profile.birthday = self.cleaned_data['birthday']
        profile.phone = self.cleaned_data['phone']


class MessageForm(BasicForm):
    target = forms.ModelChoiceField(queryset=Account.objects.all(), label="To")
    setup_field(target)
    header = forms.CharField(max_length=300)
    setup_field(header, "Message header")
    body = forms.CharField(max_length=1000)
    setup_field(body, "Message body")

    def generate(self, sender):
        return Message(
            target=self.cleaned_data['target'],
            sender=sender,
            header=self.cleaned_data['header'],
            body=self.cleaned_data['body'],
        )


class EmployeeRegistrationForm(BasicForm):
    firstname = forms.CharField(label='First Name', max_length=50)
    setup_field(firstname, 'Enter first name here')
    lastname = forms.CharField(label='Last Name', max_length=50)
    setup_field(lastname, 'Enter last name here')
    email = forms.EmailField(max_length=50, validators=[validate_username_available])
    setup_field(email, 'Enter email here')
    password_first = forms.CharField(label='Password', min_length=1, max_length=50, widget=forms.PasswordInput())
    setup_field(password_first, "Enter password here")
    password_second = forms.CharField(label='', min_length=1, max_length=50, widget=forms.PasswordInput())
    setup_field(password_second, "Enter password again")
    employee = forms.ChoiceField(required=False, choices=Account.EMPLOYEE_TYPES)
    setup_field(employee)

    def clean(self):
        """
        This is to make sure both passwords fields have the same values in them. If they don't mark
        them as errous.
        """
        cleaned_data = super(EmployeeRegistrationForm, self).clean()
        password_first = cleaned_data.get('password_first')
        password_second = cleaned_data.get('password_second')
        employee = cleaned_data.get('employee')
        if password_first and password_second and password_first != password_second:
            self.mark_error('password_second', 'Passwords do not match')
        return cleaned_data


class ImportForm(forms.Form):
    upload = forms.FileField(required=True, widget=forms.FileInput())


class ExportForm(forms.Form):
    CHOICES = (
        ('users', 'Download all users'),
    )
    export = forms.ChoiceField(required=True, widget=forms.RadioSelect, choices=CHOICES)

class StatisticsForm(BasicForm):
    startDate = forms.DateTimeField(required=True, label="Start Time")
    setup_field(startDate, "Enter as YYYY-MM-DD HH-MM")
    endDate = forms.DateTimeField(required=True, label="End Time")
    setup_field(endDate, "Enter as YYYY-MM-DD HH-MM")

    def assign(self, statistics):
        statistics.startTime = self.cleaned_data['startDate']
        statistics.endTime = self.cleaned_data['endDate']


class PropertyCreationForm(ModelForm):
    class Meta:
        model = Property
        fields = '__all__'
        exclude = ['photos', 'public_utils', 'review_count', 'overall_rating', 'owner']


class UnitCreationForm(ModelForm):
    class Meta:
        model = Unit
        fields = '__all__'
        exclude = ['property']


    def __init__(self, *args, **kwargs):
        property_id = kwargs.pop('property_id', None)
        super(UnitCreationForm, self).__init__(*args, **kwargs)
        self.fields['unitCode'].label = 'Unit Code'
        self.fields['unit_price'].label = 'Unit Price'
        self.fields['rent'].label = 'Rent'
        self.fields['floor'].label = 'Floor'
        self.fields['bedrooms'].label = 'Bedrooms'
        if property_id:
            self.fields['floor'].queryset = Floor.objects.filter(property_id=property_id)
        else:
            self.fields['floor'].queryset = Floor.objects.none()

        # widgets = {
        #     'unitCode': forms.TextInput(attrs={'class': 'form-control'}),
        #     'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
        #     'rent': forms.NumberInput(attrs={'class': 'form-control'}),
        #     'floor': forms.Select(attrs={'class': 'form-control'}),
        #     'bedrooms': forms.NumberInput(attrs={'class': 'form-control'}),
        #     'bathrooms': forms.NumberInput(attrs={'class': 'form-control'}),
        #     'size': forms.NumberInput(attrs={'class': 'form-control'}),
        #     'description': forms.Textarea(attrs={'class': 'form-control'}),
        # }


class FacilitiesForm(ModelForm):
    class Meta:
        model = Facilities
        fields = '__all__'
        widgets = {
            'property': forms.HiddenInput(),
        }


class PublicUtilsForm(ModelForm):
    class Meta:
        model = PublicUtils
        fields = "__all__"
        widgets = {
            'prop': forms.HiddenInput(),
            'mini_market': forms.NumberInput(attrs={'class': 'form-control'}),
            'hospital': forms.NumberInput(attrs={'class': 'form-control'}),
            'canteen': forms.NumberInput(attrs={'class': 'form-control'}),
            'train_station': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(PublicUtilsForm, self).__init__(*args, **kwargs)
        self.fields['mini_market'].label = 'Mini market'
        self.fields['hospital'].label = 'Hospital'
        self.fields['canteen'].label = 'Canteen'
        self.fields['train_station'].label = 'Train station'


class PropertyEditForm(ModelForm):
    class Meta:
        model = Property
        fields = ['name', 'address', 'number_of_floors', 'size', 'description', 'price', 'advanced_payment']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'number_of_floors': forms.NumberInput(attrs={'class': 'form-control'}),
            'size': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'advanced_payment': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(PropertyEditForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Property Name'
        self.fields['address'].label = 'Address'
        self.fields['number_of_floors'].label = 'Number of Floors'
        self.fields['size'].label = 'Size (sq ft)'
        self.fields['description'].label = 'Description'
        self.fields['price'].label = 'Price'
        self.fields['advanced_payment'].label = 'Advanced Payment'


class PhotoForm(ModelForm):
    class Meta:
        model = Photo
        fields = ['image']


class PropertyOwnerCreationForm(ModelForm):
    class Meta:
        model = PropertyOwner
        fields = '__all__'
        exclude = ["profile", "is_verified", "number_of_properties"]


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['next_date']
        widgets = {
            'next_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',  # HTML5 input type for date and time
                'class': 'form-control',  # Optional: Add a CSS class for styling
                'placeholder': 'Select a date and time',  # Optional: Add a placeholder
            })
        }

class PaymentForm(ModelForm):
    class Meta:
        model = PaymentDb
        fields = '__all__'
        # exclude = ['made_by', 'property_unit']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'reciever': forms.TextInput(attrs={'class': 'form-control'}),
            'sender': forms.TextInput(attrs={'class': 'form-control'}),
            'gateway': forms.Select(attrs={'class': 'form-control'}),
            'bank': forms.TextInput(attrs={'class': 'form-control'}),
            'purpose': forms.Select(attrs={'class': 'form-control'}),
        }

        def __init__(self, *args, **kwargs):
            super(PaymentForm, self).__init__(*args, **kwargs)
            self.fields['amount'].label = 'Amount'
            self.fields['reciever'].label = 'Receiver'
            self.fields['sender'].label = 'Sender'
            self.fields['gateway'].label = 'Payment Gateway'
            self.fields['bank'].label = 'Bank'
            self.fields['purpose'].label = 'Purpose'
