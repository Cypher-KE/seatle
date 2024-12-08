from datetime import datetime

from django.http import HttpResponse
from django_daraja.mpesa.core import MpesaClient

from server.forms import PaymentForm


def pay_visiting_fee(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)


        if form.is_valid():
            clean = form.cleaned_data
            print(clean)
            cl = MpesaClient()
            # Use a Safaricom phone number that you have access to, for you to be able to view the prompt.
            phone_number = clean['sender']
            amount = clean['amount']
            account_reference = 'reference'
            transaction_desc = 'Description'
            callback_url = 'https://api.darajambili.com/express-payment'
            response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
            print(response)
            # If response is a dictionary
            if isinstance(response, dict):
                for key, value in response.items():
                    print(f"{key}: {value}")
            # If response is an object with attributes
            else:
                for attribute in dir(response):
                    if not attribute.startswith('_'):
                        print(f"{attribute}: {getattr(response, attribute)}")

            if response.ok is True:
                print('nice')

            for field_name, field_value in form.cleaned_data.items():
                print(f"Field Name: {field_name}, Field Value: {field_value}")

            new_payment = form.save(commit=True)
            print(new_payment)
            #create a way to confirm payment

            return HttpResponse(response)
