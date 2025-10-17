#!/bin/bash
# Script de déploiement pour AUTO REPUBLIC RDC
# À exécuter sur votre VPS CentOS

# Configuration
PROJECT_NAME="auto-republic-rdc"
PROJECT_PATH="/var/www/car_rent"
DOMAIN="votre-domaine.com"  # Remplacez par votre domaine
NGINX_SITE="auto-republic-rdc"

echo "🚀 Déploiement de AUTO REPUBLIC RDC..."

# 1. Arrêter l'application PM2 si elle existe
echo "📦 Arrêt de l'application PM2..."
pm2 stop $PROJECT_NAME 2>/dev/null || echo "Application non trouvée"
pm2 delete $PROJECT_NAME 2>/dev/null || echo "Application non trouvée"

# 2. Aller dans le répertoire du projet
cd $PROJECT_PATH

# 3. Activer l'environnement virtuel (si vous en utilisez un)
# source venv/bin/activate  # Décommentez si nécessaire

# 4. Mettre à jour le code (si vous utilisez Git)
# git pull origin main  # Décommentez si nécessaire

# 5. Installer les dépendances
echo "📦 Installation des dépendances..."
pip install -r requirements.txt

# 6. Appliquer les migrations
echo "🗄️ Application des migrations..."
python manage.py migrate

# 7. Collecter les fichiers statiques
echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# 8. Créer le répertoire des logs
mkdir -p logs

# 9. Démarrer l'application avec PM2
echo "🚀 Démarrage de l'application avec PM2..."
pm2 start ecosystem.config.js

# 10. Sauvegarder la configuration PM2
pm2 save

# 11. Configurer PM2 pour démarrer au boot
pm2 startup

# 12. Tester la configuration Nginx
echo "🔧 Test de la configuration Nginx..."
nginx -t

# 13. Recharger Nginx
echo "🔄 Rechargement de Nginx..."
systemctl reload nginx

# 14. Vérifier le statut
echo "✅ Vérification du statut..."
pm2 status
systemctl status nginx

echo "🎉 Déploiement terminé !"
echo "🌐 Votre application est accessible sur: http://$DOMAIN"
echo "📊 Monitoring PM2: pm2 monit"
echo "📝 Logs PM2: pm2 logs $PROJECT_NAME"
echo "📝 Logs Nginx: tail -f /var/log/nginx/auto_republic_*.log"
