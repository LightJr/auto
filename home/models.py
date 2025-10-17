from django.db import models
from django.core.validators import RegexValidator

# Create your models here.

class Vehicle(models.Model):
    """Modèle pour les véhicules disponibles"""
    name = models.CharField(max_length=100)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    seats = models.IntegerField()
    luggage = models.IntegerField()
    vehicle_type = models.CharField(max_length=50)
    image = models.CharField(max_length=200)
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Reservation(models.Model):
    """Modèle pour les réservations principales"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('cancelled', 'Annulée'),
    ]
    
    # Informations du client
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Format: '+999999999'. Maximum 15 chiffres.")
    phone = models.CharField(validators=[phone_regex], max_length=17)
    
    # Informations générales de la réservation
    pickup_date = models.DateField()
    pickup_time = models.TimeField()
    return_date = models.DateField()
    return_time = models.TimeField()
    pickup_location = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    
    # Informations système
    reservation_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Réservation {self.reservation_number} - {self.first_name} {self.last_name}"
    
    @property
    def duration_days(self):
        """Calculer la durée de location en jours"""
        from datetime import datetime
        
        # Convertir les chaînes en objets date si nécessaire
        if isinstance(self.pickup_date, str):
            pickup = datetime.strptime(self.pickup_date, '%Y-%m-%d').date()
        else:
            pickup = self.pickup_date
            
        if isinstance(self.return_date, str):
            return_d = datetime.strptime(self.return_date, '%Y-%m-%d').date()
        else:
            return_d = self.return_date
            
        return (return_d - pickup).days + 1
    
    def save(self, *args, **kwargs):
        if not self.reservation_number:
            import uuid
            self.reservation_number = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

class ReservationVehicle(models.Model):
    """Modèle pour les véhicules dans une réservation"""
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='vehicles')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.reservation.reservation_number} - {self.vehicle.name}"

class Purchase(models.Model):
    """Modèle pour les achats de véhicules"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmé'),
        ('cancelled', 'Annulé'),
    ]

    # Informations du client
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Format: '+999999999'. Maximum 15 chiffres.")
    phone = models.CharField(validators=[phone_regex], max_length=17)

    # Informations générales de l'achat
    delivery_date = models.DateField()
    delivery_time = models.TimeField()
    delivery_address = models.CharField(max_length=200)
    
    PAYMENT_CHOICES = [
        ('card', 'Carte bancaire'),
        ('transfer', 'Virement bancaire'),
        ('cash', 'Espèces'),
    ]
    payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICES, default='card')

    # Informations système
    purchase_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Achat {self.purchase_number} - {self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.purchase_number:
            import uuid
            self.purchase_number = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

class PurchaseVehicle(models.Model):
    """Modèle pour les véhicules dans un achat"""
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='vehicles')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.purchase.purchase_number} - {self.vehicle.name} x{self.quantity}"

class ContactMessage(models.Model):
    """Modèle pour les messages de contact"""
    STATUS_CHOICES = [
        ('new', 'Nouveau'),
        ('read', 'Lu'),
        ('replied', 'Répondu'),
        ('closed', 'Fermé'),
    ]

    # Informations du client
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    website = models.URLField(blank=True, null=True)
    message = models.TextField()

    # Informations système
    message_slug = models.SlugField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Message {self.message_slug} - {self.name} ({self.subject})"

    def save(self, *args, **kwargs):
        if not self.message_slug:
            import uuid
            self.message_slug = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

class Newsletter(models.Model):
    """Modèle pour les abonnements à la newsletter"""
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('unsubscribed', 'Désabonné'),
        ('pending', 'En attente'),
    ]

    # Informations de l'abonné
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    
    # Informations système
    subscription_slug = models.SlugField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    subscribed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Newsletter {self.subscription_slug} - {self.email}"

    def save(self, *args, **kwargs):
        if not self.subscription_slug:
            import uuid
            self.subscription_slug = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)