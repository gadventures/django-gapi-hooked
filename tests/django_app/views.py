from hooked.views import WebhookReceiverView


class OurVeryOwnReceiverView(WebhookReceiverView):
    """
    A webhook receiver based on WebhookReceiverView for us to use in our tests.
    It's got a handler method for `places` resources and kind of decoy
    `handle_itineraries` attribute.

    See the `django_app.tests` module for those tests.
    """
    # This attribute is named like our resource handler methods, but we should
    # not try to call it like it is a function
    handle_itineraries = 'some non-callable thing'

    # A legitimate resource handler method for places resources
    def handle_places(self, event):
        pass
