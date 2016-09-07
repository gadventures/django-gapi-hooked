# django-gapi-hooked

django-gapi-hooked is a tiny library to add a [G Adventures API](https://developers.gadventures.com/) Web Hook receiver view to your code base.

## Quick Start

First, install django-gapi-hooked into your environment.

    pip install django-gapi-hooked

Then, include the receiver view into your urls.py, e.g.:

    from hooked import WebhookReceiverView

    urlpatterns = patterns('',
        url(r'^webhooks/$', WebhookReceiverView.as_view(), name='webhooks_endpoint'),
    )

Now you'll have an endpoint available at `/webhooks` that will handle a webhook
event from the G API. The view takes care of responding with a proper SHA256
key, validating the webhook event (prevents abuse!), and finally, uses Django
Signals to notify connected receivers that an event has occurred.

### Settings

To make sure webhooks are validated properly you'll need to include the following in your settings.

    GAPI_API_ROOT = 'https://rest.gadventures.com'
    GAPI_WEBHOOKS_VALIDATION_KEY = <your webhooks validation key>


## Listening to events

There are two ways you can do this. First, you can simply subclass the
`handle_webhook_event` function on `hooked.views.WebhookReceiverview`:

    from hooked import WebhookReceiverView

    class MyReceiver(WebhookReceiverView):
        def handle_webhook_event(self, event):
            # Just an example ...
            my_queue.push(event=event)


Or, you can use Signals to de-couple how webhooks are handled. This is useful
for larger projects that may handle specific resources differently. 


    from hooked import webhook_event

    from django.dispatch import receiver

    # The sender is always a resource name, so it's simple to connect a resource
    # to a specific handler.
    @receiver(webhook_event, sender="profiles")
    def my_handler(sender, event, **kwargs):
        profile_task.push(event=event)
