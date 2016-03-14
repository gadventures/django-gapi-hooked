import json
import logging
from urlparse import urljoin

from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from .signals import webhook_event

logger = logging.getLogger(__name__)

INVALID_EVENT_MESSAGE = 'Invalid event'

WEBHOOKS_VALIDATION_KEY = getattr(settings, 'GAPI_WEBHOOKS_VALIDATION_KEY', None)
API_ROOT = getattr(settings, 'GAPI_API_ROOT', None)

class WebhookReceiverView(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(WebhookReceiverView, self).dispatch(request, *args, **kwargs)

    def log_failure(self, message, **kwargs):
        logger.warning(message, extra={'body': self.request.body}, **kwargs)

    def clean_events(self, request):
        try:
            events = json.loads(request.body)
        except ValueError:
            self.log_failure('Invalid webhook POST', exc_info=True)
            return HttpResponseBadRequest('Cannot parse JSON')

        if not isinstance(events, list):
            self.log_failure('Webhook events is not a list')
            return HttpResponseBadRequest(INVALID_EVENT_MESSAGE)

        if not self.validate_events(events):
            self.log_failure('Webhook events do not validate')
            return HttpResponseBadRequest(INVALID_EVENT_MESSAGE)
        return events

    def post(self, request, *args, **kwargs):

        remote_addr = request.META['REMOTE_ADDR']

        logger.info('Received POST request from %s to webhook rece2iver',
            remote_addr, extra={'request': request})

        events = self.clean_events(request)

        for event in events:
            self._handle_webhook_event(event)

        response = HttpResponse('OK')
        response['X-Application-SHA256'] = WEBHOOKS_VALIDATION_KEY
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
            API_ROOT,
            '/'.join(path_parts)
        )
        actual = event['data']['href']

        if expected != actual:
            logger.error('Expected webhook href does not equal data (%s != %s)', expected, actual)
            return False

        return True

    def _handle_webhook_event(self, event):
        resource = event['resource']
        webhook_event.send(sender=resource, event=event)
        self.handle_webhook_event(event)

    def handle_webhook_event(self, event):
        """ Hook for handling webhook events. """
        pass
