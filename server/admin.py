from django.contrib import admin
from server.models import Account, Profile, Action
# Register your models here.
class AccountAdmin(admin.ModelAdmin):
    fields = ['role', 'profile', 'user']
    list_display = ('role', 'profile')


admin.site.register(Account, AccountAdmin)


class ProfileAdmin(admin.ModelAdmin):
    fields = [
        'firstname',
        'lastname',
        'sex',
        'birthday',
        'phone',
        'allergies'
    ]
    list_display = ('firstname', 'lastname', 'birthday', 'created')


admin.site.register(Profile, ProfileAdmin)


class ActionAdmin(admin.ModelAdmin):
    readonly_fields = ('timePerformed',)
    fields = [
        'type',
        'description',
        'account',
    ]
    list_display = ('account', 'type', 'description', 'timePerformed')
    list_filter = ('account', 'type', 'timePerformed')
    ordering = ('-timePerformed',)


admin.site.register(Action, ActionAdmin)

