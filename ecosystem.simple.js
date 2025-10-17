module.exports = {
  apps: [{
    name: 'auto-republic-rdc',
    script: 'gunicorn',
    args: '--bind 127.0.0.1:6987 --workers 3 --timeout 120 car.wsgi:application',
    cwd: '/var/www/car_rent',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      DJANGO_SETTINGS_MODULE: 'car.settings',
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true,
  }]
};
