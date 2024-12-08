from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from . import views, views_home, views_profile, views_admin, views_message, views_property, views_payment

app_name = 'server'

urlpatterns = [
    path('', views_home.login_view, name='index'),
    path('logout/', views_home.logout_view, name='logout'),
    path('register/', views_home.register_view, name='register'),
    path('setup/', views_home.setup_view, name='setup'),

    path('error/denied/', views_home.error_denied_view, name='error_denied'),

    path('admin/users/', views_admin.users_view, name='admin_users'),
    path('admin/archived_users/', views_admin.view_archived_users, name='admin_archived_users'),
    path('admin/activity/', views_admin.activity_view, name='admin_activity'),
    path('admin/statistics/', views_admin.statistic_view, name='admin_statistics'),
    path('admin/createemployee/', views_admin.createemployee_view, name='admin_createemployee'),
    path('admin/import/', views_admin.csv_import_view, name='admin_import'),
    path('admin/export/', views_admin.csv_export_view, name='admin_export'),
    path('message/list/', views_message.list_view, name='message_list'),
    path('message/new/', views_message.new_view, name='message_new'),
    path('message/read/<int:pk>/', views_message.read_message, name='read_message'),

    path('profile/', views_profile.profile_view, name='profile'),
    path('profile/update/', views_profile.update_view, name='profile_update'),
    path('profile/password/', views_profile.password_view, name='profile_password'),
    path('profile/add_owner/', views_profile.add_owner_details, name='add_owner_details'),

    path('listings', views_property.list_properties, name="listings"),
    path('owner/listings', views_property.owner_properties, name="owner_listings"),
    path('property/<str:pk>/', views_property.get_property, name='property'),
    path('new_property', views_property.new_property, name="new_property"),

    #edit property
    path('facilities/<str:pk>', views_property.property_facilities, name="facilities"),
    path('utils/<str:pk>', views_property.property_utils, name="utils"),
    path('advance_pay/<str:pk>/', views_property.advance_payment),
    path('edit/<str:pk>/', views_property.edit_property, name="edit_unit"),
    path('add_property_photos/<str:pk>/', views_property.upload_photos, name="add_prop_photos"),
    path('property_detail/<str:pk>/', views_property.property_detail, name='property_detail'),

    #unit
    path('unit/<str:pk>/', views_property.new_unit, name="new_unit"),
    path('units/<str:pk>/', views_property.get_units, name="units_list"),
    path('unit_details/<str:pk>/', views_property.get_unit, name="unit"),
    
    #bookings
    path('booking/<str:pk>/', views_property.booking, name="booking"),
    path('bookings', views_property.get_bookings, name="get_my_bookings"),
    path('unit_bookings/<str:pk>', views_property.get_unit_bookings, name="unit_bookings"),
    path('pay_booking/<str:pk>/', views_property.get_booking_form, name="pay_booking"),

    path('dev/delete_all', views_property.delete_all_properties_test),
    path('dev/payment', views_payment.pay_visiting_fee, name="pay_visiting"),

]
