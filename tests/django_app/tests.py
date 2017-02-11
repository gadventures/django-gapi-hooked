"""
Tests for a view that subclasses WebhookReceiverView
"""
import json

from django.core.exceptions import ImproperlyConfigured
from hooked.utils import compute_request_signature
from hooked.views import (
    APP_KEY_SETTING,
    ErrorMessages,
    FAIL_ON_MISMATCH_SETTING,
)
import pytest

from .urls import WEBHOOK_URL
from .views import OurVeryOwnReceiverView


# Test data ###########################################################

GOOD_EVENT_LIST = [
    {
      "event_type": "departures_services.created",
      "resource": "departure_services",
      "created": "2013-05-17T05:34:38Z",
      "data": {
          "id": "123",
          "href": "https://rest.gadventures.com/departure_services/123"
      }
    },
    {
      "event_type": "bookings.updated",
      "resource": "bookings",
      "created": "2013-05-17T05:34:38Z",
      "data": {
          "id": "123",
          "href": "https://rest.gadventures.com/bookings/123"
      }
    },
]
GOOD_EVENT_LIST_JSON = json.dumps(GOOD_EVENT_LIST)

INVALID_JSON = GOOD_EVENT_LIST_JSON.replace('{', '(')

NON_LIST_JSON = json.dumps(GOOD_EVENT_LIST[0])

MISSING_EVENT_TYPE_LIST_JSON = json.dumps([
    {
      "resource": "departure_services",
      "created": "2013-05-17T05:34:38Z",
      "data": {
          "id": "123",
          "href": "https://rest.gadventures.com/departure_services/123"
      }
    },
])

MISSING_HREF_LIST_JSON = json.dumps([
    {
      "event_type": "departures_services.created",
      "resource": "departure_services",
      "created": "2013-05-17T05:34:38Z",
      "data": {
          "id": "123",
      }
    },
])


# Test cases ##########################################################

def test_get_is_not_allowed(rf, settings):
    """ GET requests should be rejected """
    setattr(settings, APP_KEY_SETTING, '123appkey')
    view = OurVeryOwnReceiverView.as_view()
    request = rf.get(WEBHOOK_URL)
    response = view(request)

    # GET not allowed, only POSTS
    assert response.status_code == 405


def test_no_app_key(rf):
    """ If we don't set an application key we can't use the view """
    view = OurVeryOwnReceiverView.as_view()
    request = rf.get(WEBHOOK_URL)

    with pytest.raises(ImproperlyConfigured):
        response = view(request)


@pytest.mark.parametrize("resource_name,expected", [
    # No matching handler, should get the default handler.
    ('no_handler', 'handle_webhook_event'),

    # There is a handle_itineraries attribute on our view, but it's not
    # callable. We should get the default handler.
    ('itineraries', 'handle_webhook_event'),

    # We should get our custom defined handler for places resources.
    ('places', 'handle_places'),
])
def test_webhook_handler_dispatching(resource_name, expected, settings):
    """
    Test that we hit the correctly matching handler methods when processing
    events.
    """
    setattr(settings, APP_KEY_SETTING, '123appkey')
    view = OurVeryOwnReceiverView()
    event = {
        'event_type': '{}.updated'.format(resource_name),
        'resource': resource_name,
        'created': '2013-05-17T05:34:38Z',
        'data': {
            'id': '123',
            'href': 'https://rest.gadventures.com/{}/123'.format(resource_name),
        }
    }
    assert view.get_event_handler(event).__name__ == expected


@pytest.mark.parametrize('fail_on_mismatch', (True, False))
def test_bad_signature(fail_on_mismatch, settings, rf):
    """
    Test behaviour of a POST with a bad signature. We'll get different results
    here depending on settings.
    """
    app_key = '123appkey'
    setattr(settings, APP_KEY_SETTING, app_key)
    setattr(settings, FAIL_ON_MISMATCH_SETTING, fail_on_mismatch)
    view = OurVeryOwnReceiverView.as_view()
    request = rf.post(
        WEBHOOK_URL,
        GOOD_EVENT_LIST_JSON,
        content_type='application/json')

    response = view(request)
    if fail_on_mismatch:
        assert response.status_code == 400
        assert response.content == ErrorMessages.INVALID_SIGNATURE
    else:
        assert response.status_code == 200


@pytest.mark.parametrize('post_data,expected_error_message', [
    (GOOD_EVENT_LIST_JSON, None),
    (INVALID_JSON, ErrorMessages.INVALID_JSON),
    (NON_LIST_JSON, ErrorMessages.INVALID_EVENT),
    (MISSING_EVENT_TYPE_LIST_JSON, ErrorMessages.INVALID_EVENT),
    (MISSING_HREF_LIST_JSON, ErrorMessages.INVALID_EVENT),
])
def test_good_signature(post_data, expected_error_message, settings, rf):
    """
    Test behaviour of a POST with a valid signature and various payloads.
    """
    app_key = '123appkey'
    request_signature = compute_request_signature(app_key, post_data)
    setattr(settings, APP_KEY_SETTING, app_key)
    setattr(settings, FAIL_ON_MISMATCH_SETTING, True)
    view = OurVeryOwnReceiverView.as_view()
    request = rf.post(
        WEBHOOK_URL,
        post_data,
        content_type='application/json',
        HTTP_X_GAPI_SIGNATURE=request_signature)

    response = view(request)
    if expected_error_message is None:
        assert response.status_code == 200
    else:
        assert response.status_code == 400
        assert response.content == expected_error_message
