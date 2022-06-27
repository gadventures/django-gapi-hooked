try:
    from django.conf.urls import url as re_path
except ImportError:
    from django.urls import re_path

from .views import OurVeryOwnReceiverView

WEBHOOK_URL = 'webhooks/'

urlpatterns = [
    re_path(r'^{}$'.format(WEBHOOK_URL), OurVeryOwnReceiverView.as_view()),
]
