import logging
import logging.config
import os

os.makedirs("logs", exist_ok=True)

# Define logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} {name} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'main': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/main.log',  # Logs for the root app
            'mode': 'w',
            'formatter': 'verbose',
        },
        'producer': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/producer.log',
            'mode': 'w',
            'formatter': 'verbose',
        },
        'consumer': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/consumer.log',
            'mode': 'w',
            'formatter': 'verbose',
        },
        'pull': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/pull.log',
            'mode': 'w',
            'formatter': 'verbose',
        },
        'push': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/push.log',
            'mode': 'w',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {  # Root logger for the app
            'handlers': ['console', 'main'],
            'level': 'DEBUG',  # This will include all debug logs from modules
            'propagate': True,
        },
        'consumer': {
            'handlers': ['consumer'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'producer': {
            'handlers': ['producer'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'push': {
            'handlers': ['push'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'pull': {
            'handlers': ['pull'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
