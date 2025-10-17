from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Vehicle, Reservation, ReservationVehicle
from datetime import datetime, date, time
import json


class BookingTestCase(TestCase):
    def setUp(self):
        """Configuration initiale pour les tests"""
        # Créer des véhicules de test
        self.vehicle1 = Vehicle.objects.create(
            name="BMW X5",
            vehicle_type="SUV",
            price_per_day=150.00,
            seats=5,
            luggage=3,
            is_available=True
        )
        
        self.vehicle2 = Vehicle.objects.create(
            name="Mercedes C-Class",
            vehicle_type="Berline",
            price_per_day=120.00,
            seats=5,
            luggage=2,
            is_available=True
        )
        
        # Client de test
        self.client = Client()
    
    def test_create_booking_success(self):
        """Test de création de réservation réussie"""
        # Données de test
        booking_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '+1234567890',
            'pickup_date': '2025-10-20',
            'pickup_time': '10:00',
            'return_date': '2025-10-22',
            'return_time': '18:00',
            'pickup_location': 'Paris',
            'destination': 'Lyon',
            'vehicles[0][id]': str(self.vehicle1.id),
            'vehicles[0][name]': self.vehicle1.name,
            'vehicles[0][price]': str(self.vehicle1.price_per_day),
        }
        
        # Envoyer la requête POST
        response = self.client.post(reverse('create_booking'), booking_data)
        
        # Vérifier la réponse
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        if not response_data['success']:
            print(f"Erreur dans le test: {response_data['message']}")
        self.assertTrue(response_data['success'])
        
        # Vérifier que la réservation a été créée
        reservation = Reservation.objects.get(email='john.doe@example.com')
        self.assertEqual(reservation.first_name, 'John')
        self.assertEqual(reservation.last_name, 'Doe')
        self.assertEqual(reservation.total_price, 450.00)  # 150€ * 3 jours (du 20 au 22 inclus)
        
        # Vérifier que les dates sont correctement stockées
        self.assertEqual(str(reservation.pickup_date), '2025-10-20')
        self.assertEqual(str(reservation.return_date), '2025-10-22')
        self.assertIsNotNone(reservation.created_at)  # Date de soumission
        
        # Vérifier que le véhicule a été associé
        reservation_vehicle = ReservationVehicle.objects.get(reservation=reservation)
        self.assertEqual(reservation_vehicle.vehicle, self.vehicle1)
        self.assertEqual(reservation_vehicle.price_per_day, 150.00)
        self.assertEqual(reservation_vehicle.total_price, 450.00)
    
    def test_create_booking_multiple_vehicles(self):
        """Test de création de réservation avec plusieurs véhicules"""
        booking_data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'phone': '+1234567890',
            'pickup_date': '2025-10-20',
            'pickup_time': '10:00',
            'return_date': '2025-10-21',
            'return_time': '18:00',
            'pickup_location': 'Paris',
            'destination': 'Marseille',
            'vehicles[0][id]': str(self.vehicle1.id),
            'vehicles[0][name]': self.vehicle1.name,
            'vehicles[0][price]': str(self.vehicle1.price_per_day),
            'vehicles[1][id]': str(self.vehicle2.id),
            'vehicles[1][name]': self.vehicle2.name,
            'vehicles[1][price]': str(self.vehicle2.price_per_day),
        }
        
        response = self.client.post(reverse('create_booking'), booking_data)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Vérifier la réservation
        reservation = Reservation.objects.get(email='jane.smith@example.com')
        self.assertEqual(reservation.total_price, 540.00)  # (150 + 120) * 2 jours
        
        # Vérifier les véhicules associés
        reservation_vehicles = ReservationVehicle.objects.filter(reservation=reservation)
        self.assertEqual(reservation_vehicles.count(), 2)
    
    def test_create_booking_invalid_dates(self):
        """Test avec des dates invalides"""
        booking_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone': '+1234567890',
            'pickup_date': '2025-10-22',  # Date de retour avant la date de prise
            'pickup_time': '10:00',
            'return_date': '2025-10-20',
            'return_time': '18:00',
            'pickup_location': 'Paris',
            'destination': 'Lyon',
            'vehicles[0][id]': str(self.vehicle1.id),
            'vehicles[0][name]': self.vehicle1.name,
            'vehicles[0][price]': str(self.vehicle1.price_per_day),
        }
        
        response = self.client.post(reverse('create_booking'), booking_data)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('date de retour doit être après', response_data['message'])
    
    def test_create_booking_no_vehicles(self):
        """Test sans véhicules sélectionnés"""
        booking_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone': '+1234567890',
            'pickup_date': '2025-10-20',
            'pickup_time': '10:00',
            'return_date': '2025-10-22',
            'return_time': '18:00',
            'pickup_location': 'Paris',
            'destination': 'Lyon',
        }
        
        response = self.client.post(reverse('create_booking'), booking_data)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('Aucun véhicule sélectionné', response_data['message'])
    
    def test_create_booking_invalid_price(self):
        """Test avec un prix invalide"""
        booking_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone': '+1234567890',
            'pickup_date': '2025-10-20',
            'pickup_time': '10:00',
            'return_date': '2025-10-22',
            'return_time': '18:00',
            'pickup_location': 'Paris',
            'destination': 'Lyon',
            'vehicles[0][id]': str(self.vehicle1.id),
            'vehicles[0][name]': self.vehicle1.name,
            'vehicles[0][price]': 'invalid_price',  # Prix invalide
        }
        
        response = self.client.post(reverse('create_booking'), booking_data)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('Prix invalide', response_data['message'])