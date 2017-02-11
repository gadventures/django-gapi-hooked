from django.conf.urls import url

from .views import OurVeryOwnReceiverView

WEBHOOK_URL = 'webhooks/'

urlpatterns = [
    url(r'^{}$'.format(WEBHOOK_URL), OurVeryOwnReceiverView.as_view()),
]
