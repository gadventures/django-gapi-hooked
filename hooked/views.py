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

    def _add_request_data_to_log_dict(self, kwargs, request):
        """
        Given a "kwargs" dict that is destined for a logging call, insert the
        request body and headers if it looks like they're not in there already.

        The body will be inserted at kwargs['extra']['request_body'] and
        the headers will be inserted at kwargs['extra']['request_headers']
        if there isn't anything already present in those locations.
        """
        kwargs['extra'] = kwargs.get('extra', {})

        if 'request_body' not in kwargs['extra']:
            kwargs['extra']['request_body'] = request.body

        if 'request_headers' not in kwargs['extra']:
            kwargs['extra']['request_headers'] = {
                key: val
                for (key, val) in request.META.items() if key.startswith('HTTP_')
            }

    def log_error(self, *args, **kwargs):
        self._add_request_data_to_log_dict(kwargs, self.request)
        logger.error(*args, **kwargs)

    def log_warning(self, *args, **kwargs):
        self._add_request_data_to_log_dict(kwargs, self.request)
        logger.warning(*args, **kwargs)

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

        logger_args = (
            'Mismatch between computed and claimed signature of incoming '
            'events. I computed %s, but the HTTP header said I should '
            'expect to find %s',
            computed_signature,
            claimed_signature)

        if fail_on_mismatch:
            self.log_error(*logger_args)
            raise ValueError(ErrorMessages.INVALID_SIGNATURE)

        self.log_warning(*logger_args)

    def clean_events(self, request):
        self.check_webhook_signature(request)

        request_body = request.body
        if PY3_TO_35 and isinstance(request.body, bytes):
            request_body = str(request.body, encoding='utf-8')

        try:
            events = json.loads(request_body)
        except ValueError:
            self.log_error('Invalid webhook POST', exc_info=True)
            raise ValueError(ErrorMessages.INVALID_JSON)

        if not isinstance(events, list):
            self.log_error('Webhook events is not a list')
            raise ValueError(ErrorMessages.INVALID_EVENT)

        if not self.validate_events(events):
            self.log_error('Webhook events do not validate')
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
