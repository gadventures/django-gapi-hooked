import django.dispatch

# This signal provides the `event` argument to receivers.
# See https://github.com/gadventures/django-gapi-hooked#django-signals
webhook_event = django.dispatch.Signal()
