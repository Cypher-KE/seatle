from datetime import date
from django.db import models
from django.contrib.auth.models import User, AbstractBaseUser
from datetime import datetime

# Create your models here.
class Profile(models.Model):
    GENDER = (
        ('M', "Male"),
        ('F', "Female"),
    )

    @staticmethod
    def to_gender(key):
        for item in Profile.GENDER:
            if item[0] == key:
                return item[1]
        return "None"

    firstname = models.CharField(blank=True, max_length=50)
    lastname = models.CharField(blank=True, max_length=50)
    sex = models.CharField(blank=True, max_length=1, choices=GENDER)
    birthday = models.DateField(default=date(1000, 1, 1))
    phone = models.CharField(blank=True, max_length=10)
    created = models.DateTimeField(auto_now_add=True)

    def get_populated_fields(self):
        """To collect form data"""
        fields = {}
        if self.firstname is not None:
            fields['firstname'] = self.firstname
        if self.lastname is not None:
            fields['lastname'] = self.lastname
        if self.sex is not None:
            fields['sex'] = self.sex
        if not self.birthday.year == 1000:
            fields['birthday'] = self.birthday
        if self.phone is not None:
            fields['phone'] = self.phone
        return fields

    def __str__(self):
        return self.firstname + " " + self.lastname


class Account(models.Model):
    ACCOUNT_UNKNOWN = 0
    ACCOUNT_TENANT = 10
    ACCOUNT_OWNER = 20
    ACCOUNT_ADMIN = 30
    ACCOUNT_TYPES = (
        (ACCOUNT_UNKNOWN, "Unknown"),
        (ACCOUNT_OWNER, "Owner"),
        (ACCOUNT_TENANT, "Tenant"),
        (ACCOUNT_ADMIN, "Admin"),
    )
    EMPLOYEE_TYPES = (
        (ACCOUNT_TENANT, "Tenant"),
        (ACCOUNT_ADMIN, "Admin"),
        (ACCOUNT_OWNER, "Owner"),
    )

    @staticmethod
    def to_name(key):
        """
        Parses an integer value to a string representing an account role.
        :param key: The account role as a int
        :return: The string representation of the name for action
        """
        for item in Account.ACCOUNT_TYPES:
            if item[0] == key:
                return item[1]
        return "None"

    @staticmethod
    def to_value(key):
        """
        Parses an string to a integer representing an account role.
        :param key: The account role as a string
        :return: The integer representation of the account role
        """
        key = key.lower()
        for item in Account.ACCOUNT_TYPES:
            if item[1].lower() == key:
                return item[0]
        return 0

    role = models.IntegerField(default=0, choices=ACCOUNT_TYPES)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    archive = models.BooleanField(default=False)

    def __str__(self):
        if self.role == 20:
            return "Dr. " + self.profile.__str__()
        else:
            return self.profile.__str__()

    class Admin:
        list_display = (
            'role',
            'profile',
            'user',
            'archive'
        )


class Action(models.Model):
    ACTION_NONE = 0
    ACTION_ACCOUNT = 1
    ACTION_TENANT = 2
    ACTION_ADMIN = 3
    ACTION_MESSAGE = 4
    ACTION_HOUSEINFO = 5
    ACTION_TYPES = (
        (ACTION_NONE, "None"),
        (ACTION_ACCOUNT, "Account"),
        (ACTION_TENANT, "Tenant"),
        (ACTION_ADMIN, "Admin"),
        (ACTION_MESSAGE, "Message"),
        (ACTION_HOUSEINFO, "House Info"),
    )

    @staticmethod
    def to_name(key):
        """
        Parses an integer value to a string representing an action.
        :param key: The action number
        :return: The string representation of the name for action
        """
        for item in Action.ACTION_TYPES:
            if item[0] == key:
                return item[1]
        return "None"

    @staticmethod
    def to_value(key):
        """
         Parses an string to a integer representing an account role.
        :param key: The account role as a string
        :return: The integer representation of the account role
        """
        key = key.lower()
        for item in Action.ACTION_TYPES:
            if item[1].lower() == key:
                return item[0]
        return 0

    type = models.IntegerField(default=0, choices=ACTION_TYPES)
    timePerformed = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=100)
    account = models.ForeignKey(Account, related_name="actions_account", on_delete=models.CASCADE)


class Message(models.Model):
    target = models.ForeignKey(Account, related_name="message_target", on_delete=models.CASCADE)
    sender = models.ForeignKey(Account, related_name="message_sender", on_delete=models.CASCADE)
    header = models.CharField(max_length=300)
    body = models.CharField(max_length=1000)
    sender_deleted = models.BooleanField(default=False)
    target_deleted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    account = models.ForeignKey(Account, related_name="notifications_account", on_delete=models.CASCADE)
    message = models.CharField(max_length=200)
    read = models.BooleanField(default=False)
    sent_timestamp = models.DateTimeField(auto_now_add=True)
    read_timestamp = models.DateTimeField(blank=True, null=True)


class PropertyOwner(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="owner")
    company_name = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    number_of_properties = models.PositiveIntegerField(default=0)
    avatar = models.ImageField(upload_to='uploads/', null=True, blank=True)


class Property(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    size = models.PositiveIntegerField()
    number_of_floors = models.PositiveIntegerField()
    description = models.TextField()
    review_count = models.PositiveIntegerField(default=0)
    overall_rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    price = models.PositiveIntegerField()
    advanced_payment = models.PositiveIntegerField()
    public_utils = models.ManyToManyField('PublicUtils')
    owner = models.ForeignKey(PropertyOwner, null=True, on_delete=models.SET_NULL, related_name="properties")

    def get_populated_fields(self):
        """used to collect form data"""
        fields = {
            'name': self.name,
            'address': self.address,
            'bedrooms': self.bedrooms,
            'size': self.size,
            'description': self.description,
            'review_count': self.review_count,
            'overall_rating': self.overall_rating,
            'price': self.price,
            'advanced_payment': self.advanced_payment,
            'public_utils': self.public_utils,
        }
        return fields


class Floor(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="floors")
    number = models.IntegerField()

    def __str__(self):
        if self.number == 0:
            return "Ground floor"
        else:
            return str(self.number)


class Unit(models.Model):
    unitCode = models.CharField(max_length=50)
    unit_price = models.PositiveIntegerField()
    rent = models.PositiveIntegerField(null=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="units")
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name="units")
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()
    size = models.PositiveIntegerField(null=True)
    description = models.TextField()


class PublicUtils(models.Model):
    prop = models.OneToOneField(Property, on_delete=models.CASCADE, related_name="public_utilities")
    mini_market = models.PositiveIntegerField()
    hospital = models.PositiveIntegerField()
    canteen = models.PositiveIntegerField()
    train_station = models.PositiveIntegerField()

class Facilities(models.Model):
    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name="facilities")
    air_conditioner = models.BooleanField(default=False)
    kitchen = models.BooleanField(default=False)
    free_parking = models.BooleanField(default=False)
    free_wifi = models.BooleanField(default=False)
    # Additional amenities
    pool = models.BooleanField(default=False)
    gym = models.BooleanField(default=False)
    balcony = models.BooleanField(default=False)
    garden = models.BooleanField(default=False)
    laundry = models.BooleanField(default=False)
    pet_friendly = models.BooleanField(default=False)
    furnished = models.BooleanField(default=False)
    fireplace = models.BooleanField(default=False)
    security = models.BooleanField(default=False)
    elevator = models.BooleanField(default=False)
    spa = models.BooleanField(default=False)
    dishwasher = models.BooleanField(default=False)

    def __str__(self):
        return f"Facilities for {self.property.name}"



class Photo(models.Model):
    property = models.ForeignKey(Property, related_name='photos', on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='property_photos/')

    def __str__(self):
        return f"Photo for {self.property.name} ({self.id})"

class Booking(models.Model):
    VIEWING = 'VIEWING'
    DEPOSIT = 'DEPOSIT'
    MOVED_IN = 'MOVED_IN'

    LEVEL = (
        (VIEWING, "Viewing"),
        (DEPOSIT, "Deposit"),
        (MOVED_IN, "Moved in"),
    )

    @staticmethod
    def to_level(key):
        for item in Booking.LEVEL:
            if item[0] == key:
                return item[1]
        return "None"

    tenant = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="bookings")
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="bookings")
    level = models.CharField(max_length=20, choices=LEVEL, default=VIEWING)
    next_date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.tenant}, {self.unit}"


class PaymentDb(models.Model):
    TILL = 'TILL'
    BANK = 'BANK'

    GATEWAY = (
        (TILL, "till"),
        (BANK, "bank"),
    )

    @staticmethod
    def to_gateway(key):
        for item in Profile.GENDER:
            if item[0] == key:
                return item[1]
        return "None"

    made_by = models.ForeignKey(Profile, on_delete=models.SET('deleted user'), related_name="payments")
    amount = models.PositiveIntegerField()
    property_unit = models.ForeignKey(Unit, on_delete=models.SET('deleted unit'), related_name="payments")
    reciever = models.CharField(max_length=50)
    sender = models.CharField(max_length=50)
    gateway = models.CharField(max_length=20,choices=GATEWAY)
    bank = models.CharField(max_length=50, default='mpesa')
    purpose = models.CharField(max_length=20, choices=Booking.LEVEL)
    booking = models.OneToOneField(Booking, on_delete=models.SET('deleted booking'), related_name="payment")



""" def save(self, *args, **kwargs):
    self.password = make_password(self.password)
    super(PropertyOwner, self) .save(*args, **kwargs)
    """


class Statistics(models.Model):
    startDate = models.DateField()
    endDate = models.DateField()

    def get_populated_fields(self):
        """to collect form data"""
        fields = {
            'startDate': self.startDate,
            'endDate': self.endDate,
        }
        return fields
