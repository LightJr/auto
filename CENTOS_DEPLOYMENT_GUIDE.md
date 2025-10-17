# Guide de déploiement AUTO REPUBLIC RDC sur CentOS
# Configuration Nginx pour CentOS

## 📁 Emplacement des fichiers de configuration Nginx sur CentOS

### 1. Configuration principale Nginx
```bash
# Fichier principal de configuration
/etc/nginx/nginx.conf

# Répertoire des configurations de sites (à créer si nécessaire)
/etc/nginx/conf.d/
```

### 2. Installation et configuration sur CentOS

```bash
# 1. Installer Nginx
sudo yum install -y nginx

# 2. Démarrer et activer Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# 3. Copier votre configuration
sudo cp nginx_auto_republic.conf /etc/nginx/conf.d/auto-republic-rdc.conf

# 4. Tester la configuration
sudo nginx -t

# 5. Recharger Nginx
sudo systemctl reload nginx
```

### 3. Structure des fichiers sur CentOS

```
/etc/nginx/
├── nginx.conf                    # Configuration principale
├── conf.d/
│   └── auto-republic-rdc.conf   # Votre configuration
├── sites-available/              # Pas utilisé sur CentOS
└── sites-enabled/                # Pas utilisé sur CentOS
```

### 4. Configuration recommandée pour CentOS

```bash
# Créer le fichier de configuration
sudo nano /etc/nginx/conf.d/auto-republic-rdc.conf

# Contenu du fichier (copier le contenu de nginx_auto_republic.conf)
```

### 5. Commandes utiles sur CentOS

```bash
# Vérifier le statut de Nginx
sudo systemctl status nginx

# Tester la configuration
sudo nginx -t

# Recharger la configuration
sudo systemctl reload nginx

# Redémarrer Nginx
sudo systemctl restart nginx

# Voir les logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### 6. Configuration du firewall (si nécessaire)

```bash
# Ouvrir les ports HTTP et HTTPS
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 7. Vérification finale

```bash
# Vérifier que Nginx écoute sur le port 80
sudo netstat -tlnp | grep :80

# Vérifier que votre application écoute sur le port 6987
sudo netstat -tlnp | grep :6987
```
