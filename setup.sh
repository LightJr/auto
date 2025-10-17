#!/bin/bash
# Script de configuration initiale pour AUTO REPUBLIC RDC
# À exécuter sur votre VPS CentOS pour la première fois

echo "🚀 Configuration initiale de AUTO REPUBLIC RDC..."

# 1. Créer le répertoire /var/www s'il n'existe pas
sudo mkdir -p /var/www
cd /var/www

# 2. Cloner le projet (remplacez par votre URL Git)
echo "📦 Clonage du projet..."
# git clone https://github.com/votre-username/car_rent.git
# Ou si vous avez déjà le projet, copiez-le :
# sudo cp -r /path/to/local/car_rent /var/www/

# 3. Définir les permissions
echo "🔐 Configuration des permissions..."
sudo chown -R $USER:$USER /var/www/car_rent
sudo chmod -R 755 /var/www/car_rent

# 4. Aller dans le répertoire du projet
cd /var/www/car_rent

# 5. Créer l'environnement virtuel Python
echo "🐍 Création de l'environnement virtuel..."
python3 -m venv venv
source venv/bin/activate

# 6. Installer les dépendances
echo "📦 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# 7. Appliquer les migrations
echo "🗄️ Application des migrations..."
python manage.py migrate

# 8. Créer un superutilisateur (optionnel)
echo "👤 Création du superutilisateur..."
echo "Voulez-vous créer un superutilisateur ? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    python manage.py createsuperuser
fi

# 9. Collecter les fichiers statiques
echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# 10. Créer le répertoire des logs
mkdir -p logs

# 11. Installer PM2 globalement
echo "📦 Installation de PM2..."
npm install -g pm2

# 12. Copier la configuration Nginx
echo "🌐 Configuration de Nginx..."
sudo cp nginx_auto_republic.conf /etc/nginx/sites-available/auto-republic-rdc

# 13. Créer le lien symbolique
sudo ln -sf /etc/nginx/sites-available/auto-republic-rdc /etc/nginx/sites-enabled/

# 14. Tester la configuration Nginx
echo "🔧 Test de la configuration Nginx..."
sudo nginx -t

# 15. Recharger Nginx
echo "🔄 Rechargement de Nginx..."
sudo systemctl reload nginx

# 16. Démarrer l'application avec PM2
echo "🚀 Démarrage de l'application avec PM2..."
pm2 start ecosystem.config.js

# 17. Sauvegarder la configuration PM2
pm2 save

# 18. Configurer PM2 pour démarrer au boot
pm2 startup

# 19. Vérifier le statut
echo "✅ Vérification du statut..."
pm2 status
sudo systemctl status nginx

echo "🎉 Configuration initiale terminée !"
echo "🌐 Votre application est accessible sur: http://votre-domaine.com"
echo "📊 Monitoring PM2: pm2 monit"
echo "📝 Logs PM2: pm2 logs auto-republic-rdc"
echo "📝 Logs Nginx: sudo tail -f /var/log/nginx/auto_republic_*.log"
echo ""
echo "📋 Prochaines étapes :"
echo "1. Modifiez 'votre-domaine.com' dans nginx_auto_republic.conf par votre vrai domaine"
echo "2. Configurez votre base de données dans car/settings.py"
echo "3. Redémarrez l'application : pm2 restart auto-republic-rdc"
