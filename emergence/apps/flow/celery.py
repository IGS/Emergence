from __future__ import absolute_import

from celery import Celery

celery = Celery('flow.celery',
                broker='amqp://',
                backend='amqp://',
                ## list of modules to start when the worker starts
                include=['flow.executor'])

# Optional configuration, see the application user guide.
celery.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
)

if __name__ == '__main__':
    celery.start()
