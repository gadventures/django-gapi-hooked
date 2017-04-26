from __future__ import absolute_import, unicode_literals

import json
import logging
import sys
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from .signals import webhook_event
from .utils import compute_request_signature, compute_webhook_validation_key

logger = logging.getLogger(__name__)

APP_KEY_SETTING = 'GAPI_APPLICATION_KEY'
FAIL_ON_MISMATCH_SETTING = 'HOOKED_FAIL_ON_BAD_SIGNATURE'
DEFAULT_API_ROOT = 'https://rest.gadventures.com/'

# From Python 3-3.5 json.loads only accepts str (and not bytes)
PY3_TO_35 = sys.version_info[0:2] >= (3, 0) and sys.version_info[0:2] <= (3, 5)


class ErrorMessages(object):
    INVALID_EVENT = b'Invalid event'
    INVALID_SIGNATURE = b'X-Gapi-Signature header does not match computed signature'
    INVALID_JSON = b'Cannot parse JSON'


def add_validation_key_to_response(response):
    response['X-Application-SHA256'] = compute_webhook_validation_key(
        getattr(settings, APP_KEY_SETTING))


class WebhookReceiverView(View):
    def __init__(self, *args, **kwargs):
        """ Check that required settings are present. """
        if not hasattr(settings, APP_KEY_SETTING):
            raise ImproperlyConfigured(
                'You must set {} to your G API application key'.format(APP_KEY_SETTING))

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(WebhookReceiverView, self).dispatch(request, *args, **kwargs)

    def log_failure(self, message, **kwargs):
        logger.warning(message, extra={'body': self.request.body}, **kwargs)

    def check_webhook_signature(self, request):
        """
        Given a request, check that its `X-Gapi-Signature` header matches our
        own calculated hash.

        If settings.HOOKED_FAIL_ON_BAD_SIGNATURE is set to True and our
        computed signature does not match the header, an exception will be
        raised. (If it is set to False, or not set and our signatures do not
        match we just log an error.)
        """
        app_key = getattr(settings, APP_KEY_SETTING)
        fail_on_mismatch = getattr(settings, FAIL_ON_MISMATCH_SETTING, True)

        computed_signature = compute_request_signature(app_key, request.body)
        claimed_signature = request.META.get('HTTP_X_GAPI_SIGNATURE', None)

        if computed_signature == claimed_signature:
            return

        self.log_failure(
            'Mismatch between computed and claimed signature of incoming '
            'events. I computed {}, but the HTTP header said I should '
            'expect to find {}'.format(computed_signature, claimed_signature))

        if fail_on_mismatch:
            raise ValueError(ErrorMessages.INVALID_SIGNATURE)

    def clean_events(self, request):
        self.check_webhook_signature(request)

        request_body = request.body
        if PY3_TO_35 and isinstance(request.body, bytes):
            request_body = str(request.body, encoding='utf-8')

        try:
            events = json.loads(request_body)
        except ValueError:
            self.log_failure('Invalid webhook POST', exc_info=True)
            raise ValueError(ErrorMessages.INVALID_JSON)

        if not isinstance(events, list):
            self.log_failure('Webhook events is not a list')
            raise ValueError(ErrorMessages.INVALID_EVENT)

        if not self.validate_events(events):
            self.log_failure('Webhook events do not validate')
            raise ValueError(ErrorMessages.INVALID_EVENT)
        return events

    def post(self, request, *args, **kwargs):

        remote_addr = request.META['REMOTE_ADDR']

        logger.info('Received POST request from %s to webhook receiver',
            remote_addr, extra={'request': request})

        try:
            events = self.clean_events(request)
        except ValueError as v:
            response = HttpResponseBadRequest(v.args[0])
            add_validation_key_to_response(response)
            return response

        for event in events:
            self.process_event(event)

        response = HttpResponse('OK')
        add_validation_key_to_response(response)
        return response

    def validate_events(self, events):

        for event in events:
            # Webhook is delivered upon subscription
            if event.get('event_type') == 'webhook.created':
                continue

            # Check that everything needed is present
            for key in ['event_type', 'resource', 'created', 'data']:
                if event.get(key) is None:
                    return False
            for key in ['id', 'href']:
                if event['data'].get(key) is None:
                    return False

            if not self.is_valid_href(event):
                return False

        return True

    def is_valid_href(self, event):
        # Check that the href points to the right place
        path_parts = [
            event['resource'],
            event['data']['id'],
        ]
        if 'variation_id' in event['data'] and event['data']['variation_id']:
            path_parts.append(event['data']['variation_id'])

        expected = urljoin(
            getattr(settings, 'GAPI_API_ROOT', DEFAULT_API_ROOT),
            '/'.join(path_parts)
        )
        actual = event['data']['href']

        if expected != actual:
            logger.error('Expected webhook href does not equal data (%s != %s)', expected, actual)
            return False

        return True

    def process_event(self, event):
        """
        Send a signal for the given event, find and dispatch to an appropriate
        event handler.
        """
        webhook_event.send(sender=event['resource'], event=event)

        handler = self.get_event_handler(event)
        handler(event)

    def get_event_handler(self, event):
        # Find the handler for this resource
        target_handler = 'handle_{}'.format(event['resource'])
        handler = getattr(self, target_handler, None)
        if not handler or not callable(handler):
            # Whoops, no resource-specific handler found, use the default
            handler = self.handle_webhook_event

        return handler

    def handle_webhook_event(self, event):
        """ Default hook for handling webhook events. """
        pass
