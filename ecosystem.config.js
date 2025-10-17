module.exports = {
  apps: [
    {
      name: "auto-republic-rdc",
      script: "/var/www/auto/.env/bin/gunicorn",
      args: "--workers 3 --bind 127.0.0.1:6987 car.wsgi:application",
      interpreter: "/var/www/auto/.env/bin/python",
      version: "1.0.0",
      env: {
        "DJANGO_SETTINGS_MODULE": "car.settings",
        "PYTHONPATH": "/var/www/auto",
      }
    }
  ]
};
