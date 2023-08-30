# django-gapi-hooked

[![CircleCI build status](https://circleci.com/gh/gadventures/django-gapi-hooked.svg?style=svg)](https://circleci.com/gh/gadventures/django-gapi-hooked)

django-gapi-hooked is a tiny library to add a [G Adventures
API](https://developers.gadventures.com/) Web Hook receiver view to your code
base.

## Quick Start

First, install django-gapi-hooked into your environment.

    pip install -e git+git@github.com:gadventures/django-gapi-hooked.git@0.6.0#egg=django-gapi-hooked

Then, include the receiver view (or your subclassed version) into your `urls.py`,
e.g.:

    # For Django 2.0+
    from django.urls import path
    from hooked import WebhookReceiverView
    urlpatterns = [
        path('webhooks/', WebhookReceiverView.as_view(), name='webhooks_endpoint'),
    ]

    # For Django 1.11
    from django.conf.urls import url
    from hooked import WebhookReceiverView
    urlpatterns = [
        url(r'^webhooks/$', WebhookReceiverView.as_view(), name='webhooks_endpoint'),
    ]

Now you'll have an endpoint available at `/webhooks` that will handle a webhook
event from the G API. The view takes care of responding with a proper SHA256
key, validating the webhook event (prevents abuse!), and finally, dispatches
received events to the handlers that you have defined.

### Settings

To make sure webhooks are validated properly you'll need to include the
following in your settings.

    GAPI_APPLICATION_KEY = <your application key>


#### Optional


When the computed signature of the incoming webhook does not match the
signature delivered with the event data we will reject the event and log an error.

If you'd like your webhook receiver to accept incoming events with incorrect
signatures (and log a warning) include the following in your settings:

    HOOKED_FAIL_ON_BAD_SIGNATURE = False


## Handling events

There are two ways you can do this: by subclassing `hooked.WebhookReceiverView`
and adding/overriding some of its methods, or by using Django's signals
framework. You probably do not want to use both of these methods.

### Subclassing `WebhookReceiverView`

The simplest implementation just overrides the `handle_webhook_event`
method:

    from hooked import WebhookReceiverView

    class MyReceiver(WebhookReceiverView):
        def handle_webhook_event(self, event):
            # Just an example ...
            my_queue.push(event=event)

In the above example, `MyReceiver.handle_webhook_event` would be called with
each incoming event.

You can also break up the handlers logically by resource -- useful if (for
example) you must perform different steps for an `itineraries`-resource event
versus a `profiles`-resource event. When processing a webhook event,
`WebhookReceiverView` will attempt to send it to `self.handle_<resource_name>`
-- for instance, `handle_itineraries` or `handle_profiles`. If no
resource-specific handler is found, we default to using `handle_webhook_event`:

    from hooked import WebhookReceiverView

    class MyReceiver(WebhookReceiverView):
        def handle_profiles(self, event):
            # Do some profile-specific things...
            profile_task.push(event=event)

        def handle_webhook_event(self, event):
            # Every non-profile resource would be handled here ...
            my_queue.push(event=event)

In the above example, `MyReceiver.handle_profiles` will be called with
any incoming events about `profiles` resources, while hooks for any other
resource types will be handled by `MyReceiver.handle_webhook_event`.

### Django signals

If you do not want to create a subclass of `WebhookReceiverView` to handle
webhooks, you can use [Django
signals](https://docs.djangoproject.com/en/1.10/topics/signals/). When a
webhook event comes in to `WebhookReceiverView` we will trigger a
`hooked.webhook_event` signal, the "sender" of the signal will be the
resource type of the webhook event.

The following is an example of how to register a function to handle hooks for
`profiles` resources.

    from hooked import webhook_event

    from django.dispatch import receiver

    # The sender is always a resource name, so it's simple to connect a resource
    # to a specific handler.
    @receiver(webhook_event, sender="profiles")
    def my_handler(sender, event, **kwargs):
        profile_task.push(event=event)

## Running tests

    tox
