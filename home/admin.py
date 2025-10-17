from django.contrib import admin
from .models import Vehicle, Reservation, ReservationVehicle, Purchase, PurchaseVehicle, ContactMessage, Newsletter

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['name', 'vehicle_type', 'price_per_day', 'seats', 'luggage', 'is_available']
    list_filter = ['vehicle_type', 'is_available']
    search_fields = ['name', 'vehicle_type']
    list_editable = ['price_per_day', 'is_available']
    ordering = ['name']

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['reservation_number', 'first_name', 'last_name', 'email', 'pickup_date', 'return_date', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'pickup_date', 'created_at']
    search_fields = ['reservation_number', 'first_name', 'last_name', 'email']
    readonly_fields = ['reservation_number', 'created_at', 'updated_at']
    date_hierarchy = 'pickup_date'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informations client', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Détails de la réservation', {
            'fields': ('pickup_date', 'pickup_time', 'return_date', 'return_time', 'pickup_location', 'destination')
        }),
        ('Informations système', {
            'fields': ('reservation_number', 'status', 'total_price', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ReservationVehicle)
class ReservationVehicleAdmin(admin.ModelAdmin):
    list_display = ['reservation', 'vehicle', 'price_per_day', 'total_price']
    list_filter = ['vehicle__vehicle_type']
    search_fields = ['reservation__reservation_number', 'vehicle__name']
    readonly_fields = ['total_price']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('reservation', 'vehicle')

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['purchase_number', 'first_name', 'last_name', 'email', 'delivery_date', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'delivery_date', 'created_at']
    search_fields = ['purchase_number', 'first_name', 'last_name', 'email']
    readonly_fields = ['purchase_number', 'created_at', 'updated_at']
    date_hierarchy = 'delivery_date'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informations client', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Détails de l\'achat', {
            'fields': ('delivery_date', 'delivery_time', 'delivery_address', 'payment_method')
        }),
        ('Informations système', {
            'fields': ('purchase_number', 'status', 'total_price', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PurchaseVehicle)
class PurchaseVehicleAdmin(admin.ModelAdmin):
    list_display = ['purchase', 'vehicle', 'price', 'quantity']
    list_filter = ['vehicle__vehicle_type']
    search_fields = ['purchase__purchase_number', 'vehicle__name']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('purchase', 'vehicle')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['message_slug', 'name', 'email', 'subject', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['message_slug', 'name', 'email', 'subject']
    readonly_fields = ['message_slug', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informations du client', {
            'fields': ('name', 'email', 'website')
        }),
        ('Contenu du message', {
            'fields': ('subject', 'message')
        }),
        ('Informations système', {
            'fields': ('message_slug', 'status', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['subscription_slug', 'email', 'first_name', 'last_name', 'status', 'subscribed_at']
    list_filter = ['status', 'subscribed_at']
    search_fields = ['subscription_slug', 'email', 'first_name', 'last_name']
    readonly_fields = ['subscription_slug', 'subscribed_at', 'updated_at']
    date_hierarchy = 'subscribed_at'
    ordering = ['-subscribed_at']
    
    fieldsets = (
        ('Informations de l\'abonné', {
            'fields': ('email', 'first_name', 'last_name')
        }),
        ('Informations système', {
            'fields': ('subscription_slug', 'status', 'subscribed_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)
