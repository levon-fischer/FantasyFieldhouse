import os
from logging.config import dictConfig


class Config:
    # Database configuration
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "SQLALCHEMY_DATABASE_URI"
    ) or "sqlite:///" + os.path.join(BASE_DIR, "fantasyApp.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.environ.get("SECRET_KEY")

    # Email configuration
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("EMAIL_USER")
    MAIL_PASSWORD = os.environ.get("EMAIL_PASS")

    # Celery configuration
    CELERY = dict(
        broker_url=os.environ.get("CELERY_BROKER_URL"),
        result_backend=os.environ.get("CELERY_RESULT_BACKEND"),
        task_ignore_result=True,
    )

    # Logging configuration
    log_directory = os.path.join(BASE_DIR, "logs")
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                },
                "detailed": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s [%(pathname)s:%(lineno)d]: %(message)s",
                },
            },
            "handlers": {
                "wsgi": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://flask.logging.wsgi_errors_stream",
                    "formatter": "default",
                    "level": "DEBUG",
                },
                "file": {
                    "class": "logging.FileHandler",
                    "filename": os.path.join(log_directory, "application.log"),
                    "formatter": "detailed",
                    "level": "INFO",
                },
                "sqlalchemy_file": {
                    "level": "DEBUG",
                    "class": "logging.FileHandler",
                    "filename": os.path.join(log_directory, "sqlalchemy.log"),
                    "formatter": "detailed",
                },
            },
            "root": {"level": "INFO", "handlers": ["wsgi", "file"]},
            "loggers": {
                "sqlalchemy": {
                    "level": "DEBUG",
                    "handlers": ["sqlalchemy_file"],
                    "propagate": False,
                }
            },
        }
    )
