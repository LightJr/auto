from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('models/', views.models, name='models'),
    path('garage/', views.garage, name='garage'),
    path('create-booking/', views.create_booking, name='create_booking'),
    path('create-purchase/', views.create_purchase, name='create_purchase'),
    path('create-contact-message/', views.create_contact_message, name='create_contact_message'),
    path('create-newsletter-subscription/', views.create_newsletter_subscription, name='create_newsletter_subscription'),
]
