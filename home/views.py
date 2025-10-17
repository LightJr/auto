from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import send_mail, get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from .models import Vehicle, Reservation, ReservationVehicle, Purchase, PurchaseVehicle, ContactMessage, Newsletter
import logging
import uuid
from datetime import datetime

# Create your views here.

def index(request):
    """Page d'accueil"""
    return render(request, 'index.html')

def about(request):
    """Page À propos"""
    return render(request, 'about.html')



def contact(request):
    """Page Contact"""
    return render(request, 'contact.html')


def models(request):
    """Page Modèles de véhicules"""
    from .models import Vehicle
    vehicles = Vehicle.objects.filter(is_available=True)
    return render(request, 'models.html', {'vehicles': vehicles})


def garage(request):
    """Page Garage"""
    return render(request, 'garage.html')

def create_booking(request):
    """Créer une réservation"""
    if request.method == 'POST':
        from .models import Vehicle, Reservation, ReservationVehicle
        from django.http import JsonResponse
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.conf import settings
        from datetime import datetime
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            # Récupérer les données du formulaire
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            pickup_date = request.POST.get('pickup_date')
            pickup_time = request.POST.get('pickup_time')
            return_date = request.POST.get('return_date')
            return_time = request.POST.get('return_time')
            pickup_location = request.POST.get('pickup_location')
            destination = request.POST.get('destination')
            
            logger.info(f"Données reçues - pickup_date: {pickup_date} (type: {type(pickup_date)}), return_date: {return_date} (type: {type(return_date)})")
            
            # Récupérer les véhicules sélectionnés
            vehicles_data = []
            index = 0
            while f'vehicles[{index}][id]' in request.POST:
                vehicle_id = request.POST.get(f'vehicles[{index}][id]')
                vehicle_name = request.POST.get(f'vehicles[{index}][name]')
                vehicle_price_str = request.POST.get(f'vehicles[{index}][price]')
                
                logger.info(f"Véhicule {index} - price_str: {vehicle_price_str} (type: {type(vehicle_price_str)})")
                
                try:
                    vehicle_price = float(vehicle_price_str)
                except (ValueError, TypeError) as e:
                    logger.error(f"Erreur conversion prix véhicule {index}: {e}")
                    return JsonResponse({
                        'success': False,
                        'message': f'Prix invalide pour le véhicule {vehicle_name}: {vehicle_price_str}'
                    })
                
                vehicles_data.append({
                    'id': vehicle_id,
                    'name': vehicle_name,
                    'price': vehicle_price
                })
                index += 1
            
            if not vehicles_data:
                return JsonResponse({
                    'success': False,
                    'message': 'Aucun véhicule sélectionné'
                })
            
            # Calculer la durée
            if not pickup_date or not return_date:
                return JsonResponse({
                    'success': False,
                    'message': 'Les dates de prise en charge et de retour sont obligatoires'
                })
            
            try:
                pickup = datetime.strptime(pickup_date, '%Y-%m-%d').date()
                return_d = datetime.strptime(return_date, '%Y-%m-%d').date()
                logger.info(f"Dates converties - pickup: {pickup} (type: {type(pickup)}), return_d: {return_d} (type: {type(return_d)})")
                
                # Validation des dates
                if return_d < pickup:
                    return JsonResponse({
                        'success': False,
                        'message': 'La date de retour doit être après la date de prise en charge'
                    })
                
                # Si même jour, vérifier les heures
                if return_d == pickup:
                    pickup_time_obj = datetime.strptime(pickup_time, '%H:%M').time()
                    return_time_obj = datetime.strptime(return_time, '%H:%M').time()
                    
                    if return_time_obj <= pickup_time_obj:
                        return JsonResponse({
                            'success': False,
                            'message': 'Pour une location d\'une journée, l\'heure de retour doit être après l\'heure de prise en charge'
                        })
                
                diff_days = (return_d - pickup).days + 1
                logger.info(f"Durée calculée: {diff_days} jours")
                
                if diff_days <= 0:
                    return JsonResponse({
                        'success': False,
                        'message': 'La durée de location doit être d\'au moins 1 jour'
                    })
            except ValueError as e:
                logger.error(f"Erreur conversion dates: {e}")
                return JsonResponse({
                    'success': False,
                    'message': f'Format de date ou heure invalide: {str(e)}'
                })
            
            # Calculer le prix total
            total_price = sum(vehicle['price'] * diff_days for vehicle in vehicles_data)
            logger.info(f"Prix total calculé: {total_price}")
            
            # Créer la réservation principale
            logger.info("Création de la réservation principale...")
            reservation = Reservation.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                pickup_date=pickup,  # Utiliser l'objet date converti
                pickup_time=pickup_time,
                return_date=return_d,  # Utiliser l'objet date converti
                return_time=return_time,
                pickup_location=pickup_location,
                destination=destination,
                total_price=total_price
            )
            logger.info(f"Réservation créée avec l'ID: {reservation.id}")
            
            # Créer les réservations de véhicules
            logger.info("Création des réservations de véhicules...")
            for vehicle_data in vehicles_data:
                logger.info(f"Traitement du véhicule: {vehicle_data}")
                vehicle = Vehicle.objects.get(id=vehicle_data['id'])
                logger.info(f"Véhicule trouvé: {vehicle.name}, prix par jour: {vehicle.price_per_day}")
                
                reservation_vehicle = ReservationVehicle.objects.create(
                    reservation=reservation,
                    vehicle=vehicle,
                    price_per_day=vehicle_data['price'],
                    total_price=vehicle_data['price'] * diff_days
                )
                logger.info(f"ReservationVehicle créé avec l'ID: {reservation_vehicle.id}")
            
            logger.info("Envoi de l'email de confirmation...")
            # Envoyer l'email de confirmation
            send_booking_confirmation_email(reservation)
            
            logger.info("Réservation terminée avec succès")
            return JsonResponse({
                'success': True,
                'message': 'Réservation créée avec succès',
                'reservation_number': reservation.reservation_number
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erreur lors de la création de la réservation: {str(e)}'
            })
    
def create_purchase(request):
    """Créer un achat"""
    if request.method == 'POST':
        from .models import Vehicle, Purchase, PurchaseVehicle
        from django.http import JsonResponse
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.conf import settings
        from datetime import datetime
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            # Récupérer les données du formulaire
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            delivery_date = request.POST.get('delivery_date')
            delivery_time = request.POST.get('delivery_time')
            delivery_address = request.POST.get('delivery_address')
            payment_method = request.POST.get('payment_method')
            
            logger.info(f"Données d'achat reçues - delivery_date: {delivery_date} (type: {type(delivery_date)})")
            
            # Récupérer les véhicules sélectionnés
            vehicles_data = []
            index = 0
            while f'vehicles[{index}][id]' in request.POST:
                vehicle_id = request.POST.get(f'vehicles[{index}][id]')
                vehicle_name = request.POST.get(f'vehicles[{index}][name]')
                vehicle_price_str = request.POST.get(f'vehicles[{index}][price]')
                vehicle_quantity_str = request.POST.get(f'vehicles[{index}][quantity]', '1')
                
                logger.info(f"Véhicule achat {index} - price_str: {vehicle_price_str} (type: {type(vehicle_price_str)}), quantity: {vehicle_quantity_str}")
                
                try:
                    vehicle_price = float(vehicle_price_str)
                    vehicle_quantity = int(vehicle_quantity_str)
                except (ValueError, TypeError) as e:
                    logger.error(f"Erreur conversion prix/quantité véhicule achat {index}: {e}")
                    return JsonResponse({
                        'success': False,
                        'message': f'Prix ou quantité invalide pour le véhicule {vehicle_name}: {vehicle_price_str}/{vehicle_quantity_str}'
                    })
                
                vehicles_data.append({
                    'id': vehicle_id,
                    'name': vehicle_name,
                    'price': vehicle_price,
                    'quantity': vehicle_quantity
                })
                index += 1
            
            if not vehicles_data:
                return JsonResponse({
                    'success': False,
                    'message': 'Aucun véhicule sélectionné'
                })
            
            # Validation de la date de livraison
            if not delivery_date:
                return JsonResponse({
                    'success': False,
                    'message': 'La date de livraison est obligatoire'
                })
            
            try:
                delivery_d = datetime.strptime(delivery_date, '%Y-%m-%d').date()
                logger.info(f"Date de livraison convertie: {delivery_d} (type: {type(delivery_d)})")
                
                # Vérifier que la date de livraison n'est pas dans le passé
                from datetime import date
                if delivery_d < date.today():
                    return JsonResponse({
                        'success': False,
                        'message': 'La date de livraison ne peut pas être dans le passé'
                    })
                    
            except ValueError as e:
                logger.error(f"Erreur conversion date de livraison: {e}")
                return JsonResponse({
                    'success': False,
                    'message': f'Format de date invalide: {str(e)}'
                })
            
            # Calculer le prix total
            total_price = sum(vehicle['price'] * vehicle['quantity'] for vehicle in vehicles_data)
            logger.info(f"Prix total achat calculé: {total_price}")
            
            # Créer l'achat principal
            logger.info("Création de l'achat principal...")
            purchase = Purchase.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                delivery_date=delivery_d,
                delivery_time=delivery_time,
                delivery_address=delivery_address,
                payment_method=payment_method,
                total_price=total_price
            )
            logger.info(f"Achat créé avec l'ID: {purchase.id}")
            
            # Créer les achats de véhicules
            logger.info("Création des achats de véhicules...")
            for vehicle_data in vehicles_data:
                logger.info(f"Traitement du véhicule achat: {vehicle_data}")
                vehicle = Vehicle.objects.get(id=vehicle_data['id'])
                logger.info(f"Véhicule trouvé: {vehicle.name}, prix: {vehicle.price_per_day}, quantité: {vehicle_data['quantity']}")
                
                purchase_vehicle = PurchaseVehicle.objects.create(
                    purchase=purchase,
                    vehicle=vehicle,
                    price=vehicle_data['price'],
                    quantity=vehicle_data['quantity']
                )
                logger.info(f"PurchaseVehicle créé avec l'ID: {purchase_vehicle.id}")
            
            logger.info("Envoi de l'email de confirmation d'achat...")
            # Envoyer l'email de confirmation
            send_purchase_confirmation_email(purchase)
            
            logger.info("Achat terminé avec succès")
            return JsonResponse({
                'success': True,
                'message': 'Achat créé avec succès',
                'purchase_number': purchase.purchase_number
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'achat: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Erreur lors de la création de l\'achat: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

def send_purchase_confirmation_email(purchase):
    """Envoyer l'email de confirmation d'achat"""
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.conf import settings
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Créer le contenu HTML de l'email
        html_content = render_to_string('emails/purchase_confirmation.html', {
            'purchase': purchase
        })
        
        logger.info(f"Tentative d'envoi d'email d'achat à {purchase.email}")
        
        # Envoyer l'email
        send_mail(
            subject=f'Confirmation d\'achat - {purchase.purchase_number}',
            message='',  # Version texte vide car on utilise HTML
            html_message=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[purchase.email],
            fail_silently=False,
        )
        
        logger.info("Email d'achat envoyé avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email d'achat: {str(e)}")
        # Ne pas faire échouer l'achat si l'email ne peut pas être envoyé
        try:
            # Essayer avec le backend console en cas d'échec SMTP
            from django.core.mail import get_connection
            from django.core.mail.message import EmailMultiAlternatives
            
            connection = get_connection('django.core.mail.backends.console.EmailBackend')
            email = EmailMultiAlternatives(
                subject=f'Confirmation d\'achat - {purchase.purchase_number}',
                body='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[purchase.email],
                connection=connection
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            logger.info("Email d'achat envoyé via le backend console")
        except Exception as console_error:
            logger.error(f"Erreur même avec le backend console: {str(console_error)}")
            # En dernier recours, afficher le contenu de l'email dans les logs
            logger.info(f"Contenu de l'email d'achat pour {purchase.email}:")
            logger.info(html_content)

def send_booking_confirmation_email(reservation):
    """Envoyer l'email de confirmation de réservation"""
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.conf import settings
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Créer le contenu HTML de l'email
        html_content = render_to_string('emails/booking_confirmation.html', {
            'reservation': reservation
        })
        
        logger.info(f"Tentative d'envoi d'email à {reservation.email}")
        
        # Envoyer l'email
        send_mail(
            subject=f'Confirmation de réservation - {reservation.reservation_number}',
            message='',  # Version texte vide car on utilise HTML
            html_message=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reservation.email],
            fail_silently=False,
        )
        
        logger.info("Email envoyé avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email: {str(e)}")
        # Ne pas faire échouer la réservation si l'email ne peut pas être envoyé
        # L'email sera affiché dans la console en mode développement
        try:
            # Essayer avec le backend console en cas d'échec SMTP
            from django.core.mail import get_connection
            from django.core.mail.message import EmailMultiAlternatives
            
            connection = get_connection('django.core.mail.backends.console.EmailBackend')
            email = EmailMultiAlternatives(
                subject=f'Confirmation de réservation - {reservation.reservation_number}',
                body='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[reservation.email],
                connection=connection
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            logger.info("Email envoyé via le backend console")
        except Exception as console_error:
            logger.error(f"Erreur même avec le backend console: {str(console_error)}")
            # En dernier recours, afficher le contenu de l'email dans les logs
            logger.info(f"Contenu de l'email pour {reservation.email}:")
            logger.info(html_content)

def create_contact_message(request):
    """Vue pour traiter les messages de contact"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})
    
    logger = logging.getLogger(__name__)
    
    try:
        # Récupérer les données du formulaire
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        website = request.POST.get('website', '').strip()
        message = request.POST.get('message', '').strip()
        
        logger.info(f"Données de contact reçues - name: {name}, email: {email}, subject: {subject}")
        
        # Validation des champs obligatoires
        if not name:
            return JsonResponse({'success': False, 'message': 'Le nom est obligatoire'})
        if not email:
            return JsonResponse({'success': False, 'message': 'L\'email est obligatoire'})
        if not subject:
            return JsonResponse({'success': False, 'message': 'Le sujet est obligatoire'})
        if not message:
            return JsonResponse({'success': False, 'message': 'Le message est obligatoire'})
        
        # Créer le message de contact
        contact_message = ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            website=website if website else None,
            message=message
        )
        
        logger.info(f"Message de contact créé avec l'ID: {contact_message.id}")
        
        # Envoyer l'email de confirmation
        send_contact_confirmation_email(contact_message)
        
        logger.info("Message de contact terminé avec succès")
        
        return JsonResponse({
            'success': True,
            'message': 'Votre message a été envoyé avec succès ! Nous vous répondrons dans les plus brefs délais.',
            'message_slug': contact_message.message_slug
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la création du message de contact: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de l\'envoi du message: {str(e)}'
        })

def send_contact_confirmation_email(contact_message):
    """Envoyer l'email de confirmation pour le message de contact"""
    logger = logging.getLogger(__name__)
    
    try:
        # Rendre le template HTML
        html_content = render_to_string('emails/contact_confirmation.html', {
            'contact_message': contact_message
        })
        
        logger.info(f"Tentative d'envoi d'email de contact à {contact_message.email}")
        
        # Essayer d'envoyer via SMTP
        try:
            connection = get_connection()
            email = EmailMultiAlternatives(
                subject=f'Confirmation de réception - {contact_message.subject}',
                body='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[contact_message.email],
                connection=connection
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            logger.info("Email de contact envoyé avec succès")
        except Exception as smtp_error:
            logger.warning(f"Erreur SMTP pour l'email de contact: {str(smtp_error)}")
            # Fallback vers le backend console
            connection = get_connection('django.core.mail.backends.console.EmailBackend')
            email = EmailMultiAlternatives(
                subject=f'Confirmation de réception - {contact_message.subject}',
                body='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[contact_message.email],
                connection=connection
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            logger.info("Email de contact envoyé via le backend console")
    except Exception as console_error:
        logger.error(f"Erreur même avec le backend console pour l'email de contact: {str(console_error)}")

def create_newsletter_subscription(request):
    """Vue pour traiter les abonnements à la newsletter"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})
    
    logger = logging.getLogger(__name__)
    
    try:
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        
        logger.info(f"Données de newsletter reçues - email: {email}, first_name: {first_name}")
        
        if not email:
            return JsonResponse({'success': False, 'message': 'L\'email est obligatoire'})
        
        # Vérifier si l'email existe déjà
        existing_subscription = Newsletter.objects.filter(email=email).first()
        if existing_subscription:
            if existing_subscription.status == 'active':
                return JsonResponse({'success': False, 'message': 'Cette adresse email est déjà abonnée à notre newsletter.'})
            elif existing_subscription.status == 'unsubscribed':
                # Réactiver l'abonnement
                existing_subscription.status = 'active'
                existing_subscription.first_name = first_name if first_name else existing_subscription.first_name
                existing_subscription.last_name = last_name if last_name else existing_subscription.last_name
                existing_subscription.save()
                logger.info(f"Abonnement réactivé pour l'email: {email}")
            else:
                # Mettre à jour les informations
                existing_subscription.status = 'active'
                existing_subscription.first_name = first_name if first_name else existing_subscription.first_name
                existing_subscription.last_name = last_name if last_name else existing_subscription.last_name
                existing_subscription.save()
                logger.info(f"Abonnement mis à jour pour l'email: {email}")
        else:
            # Créer un nouvel abonnement
            newsletter = Newsletter.objects.create(
                email=email,
                first_name=first_name if first_name else None,
                last_name=last_name if last_name else None
            )
            logger.info(f"Abonnement newsletter créé avec l'ID: {newsletter.id}")
        
        # Envoyer l'email de confirmation
        send_newsletter_confirmation_email(email, first_name, last_name)
        
        logger.info("Abonnement newsletter terminé avec succès")
        
        return JsonResponse({
            'success': True,
            'message': 'Merci ! Vous êtes maintenant abonné(e) à notre newsletter. Vous recevrez nos dernières actualités par email.'
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de l'abonnement à la newsletter: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de l\'abonnement: {str(e)}'
        })

def send_newsletter_confirmation_email(email, first_name=None, last_name=None):
    """Envoyer l'email de confirmation pour l'abonnement newsletter"""
    logger = logging.getLogger(__name__)
    
    try:
        # Construire le nom complet
        full_name = ""
        if first_name and last_name:
            full_name = f"{first_name} {last_name}"
        elif first_name:
            full_name = first_name
        elif last_name:
            full_name = last_name
        
        html_content = render_to_string('emails/newsletter_confirmation.html', {
            'email': email,
            'full_name': full_name,
            'first_name': first_name or 'Client',
            'subscribed_at': timezone.now()
        })
        
        logger.info(f"Tentative d'envoi d'email newsletter à {email}")
        
        try:
            connection = get_connection()
            email_obj = EmailMultiAlternatives(
                subject='Bienvenue dans notre newsletter AUTO REPUBLIC !',
                body='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
                connection=connection
            )
            email_obj.attach_alternative(html_content, "text/html")
            email_obj.send()
            logger.info("Email newsletter envoyé avec succès")
        except Exception as smtp_error:
            logger.warning(f"Erreur SMTP pour l'email newsletter: {str(smtp_error)}")
            # Fallback vers le backend console
            connection = get_connection('django.core.mail.backends.console.EmailBackend')
            email_obj = EmailMultiAlternatives(
                subject='Bienvenue dans notre newsletter AUTO REPUBLIC !',
                body='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
                connection=connection
            )
            email_obj.attach_alternative(html_content, "text/html")
            email_obj.send()
            logger.info("Email newsletter envoyé via le backend console")
    except Exception as console_error:
        logger.error(f"Erreur même avec le backend console pour l'email newsletter: {str(console_error)}")