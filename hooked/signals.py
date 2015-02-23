import django.dispatch

webhook_event = django.dispatch.Signal(providing_args=["event"])
