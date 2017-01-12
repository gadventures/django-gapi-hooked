import pytest

from hooked.views import WebhookReceiverView


class WHReceiverViewWithSomeHandlers(WebhookReceiverView):
    """
    A webhook receiver view plus some resource-specific handler functions, see
    test_webhook_handler_dispatching, below.
    """
    handle_itineraries = 'some non-callable thing'

    def handle_places(self, event):
        pass

test_view = WHReceiverViewWithSomeHandlers()


@pytest.mark.parametrize("resource_name,expected", [
    # No matching handler, should get the default handler.
    ('no_handler', test_view.handle_webhook_event),

    # There is a handle_itineraries attribute on our view, but it's not
    # callable. We should get the default handler.
    ('itineraries', test_view.handle_webhook_event),

    # We should get our custom defined handler for places resources.
    ('places', test_view.handle_places),
])
def test_webhook_handler_dispatching(resource_name, expected):
    """
    Test that we hit the correctly matching handler methods when processing
    events.
    """
    event = {
        'event_type': '{}.updated'.format(resource_name),
        'resource': resource_name,
        'created': '2013-05-17T05:34:38Z',
        'data': {
            'id': '123',
            'href': 'https://rest.gadventures.com/{}/123'.format(resource_name),
        }
    }
    assert test_view.get_event_handler(event) == expected
