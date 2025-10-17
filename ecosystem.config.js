module.exports = {
  apps: [{
    name: 'auto-republic-rdc',
    script: 'gunicorn',
    args: '--bind 127.0.0.1:6987 --workers 3 --timeout 120 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100 car.wsgi:application',
    cwd: '/var/www/car_rent',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      DJANGO_SETTINGS_MODULE: 'car.settings',
      PYTHONPATH: '/var/www/car_rent',
    },
    env_production: {
      NODE_ENV: 'production',
      DJANGO_SETTINGS_MODULE: 'car.settings',
      PYTHONPATH: '/var/www/car_rent',
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true,
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    kill_timeout: 5000,
    wait_ready: true,
    listen_timeout: 10000,
  }]
};
