from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.worker.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    beat_schedule={
        'update-crypto-prices-every-30-mins': {
            'task': 'app.worker.tasks.update_all_crypto_prices',
            'schedule': 60.0,

        },
    },
)

if __name__ == "__main__":
    celery_app.start()
