# -*- coding: utf-8 -*-

import pytest

from hooked.utils import compute_request_signature, compute_webhook_validation_key


@pytest.mark.parametrize("app_key,request_body", [
    # Matching types for both args
    (str('str app key'), str('str request body')),
    (u'unicode app key', u'unicode request body'),

    # Mismatched types for the args
    (str('str app key'), u'unicode request body'),
    (u'unicode app key', str('str request body')),

    # Including special characters (really this should never come up for the
    # app key... should only contain digits and a-f as it is a hex string)
    (str('str app key'), u'ʎpoq ʇsǝnbǝɹ ǝpoɔᴉun'),
    (u'ʎǝʞ ddɐ ǝpoɔᴉun', str('str request body')),
    (u'ʎǝʞ ddɐ ǝpoɔᴉun', u'ʎpoq ʇsǝnbǝɹ ǝpoɔᴉun'),
])
def test_compute_request_signature_handles_unicode_and_str(app_key, request_body):
    """
    Test that compute_request_signature doesn't explode when given both unicode
    and str inputs.
    """
    compute_request_signature(app_key, request_body)


@pytest.mark.parametrize("app_key", [
    # Bytestring/Unicode with only ASCII chars
    str('str app key'),
    u'unicode app key',

    # Non-ASCII chars! (really this should never come up because app keys
    # should only contain digits and a-f as they are hex strings)
    u'ʎǝʞ ddɐ ǝpoɔᴉun',
])
def test_compute_webhook_validation_key_handles_unicode_and_str(app_key):
    """
    Test that compute_webhook_validation_key doesn't explode when given unicode
    or str input.
    """
    compute_webhook_validation_key(app_key)
