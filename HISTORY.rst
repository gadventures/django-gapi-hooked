.. :changelog:

History
=======

Unreleased
----------
* Settings change: ``HOOKED_FAIL_ON_BAD_SIGNATURE`` now defaults to ``True``
  instead of to ``False``. Note that this means your receiver view will reject
  webhooks with incorrect signatures.

  If you find that this is happening in production, please ensure that your
  webhook subscription is using the same application key as is defined in your
  ``GAPI_APPLICATION_KEY``.

0.4.1 (2017-09-05)
------------------
* Use `exec` to read the `hooked/version.py` file in order to load in the
  `__version__` variable in `setup.py` (via PRs #15 / #16)
* Add Travis CI config file to enable testing on Travis (via PR #17)
    * Add the travis build status to the README.md file

0.4.0 (2017-06-26)
------------------
* Add Python 3.5+ support (maintaining Python 2.7 support)
* Add MIT License, begin preparing ``setup.py`` for a release on PyPI
* Add resource-name-based dynamic dispatch to ``WebhookReceiverView`` (e.g you
  can define a ``handle_profiles`` method on your subclass and it will handle
  ``profiles`` events without having to write your own routing code, see README
  for examples)
* Add a (presently very small) test suite and a ``tox.ini`` to test multiple
  Python/Django versions
* Settings changes:
    * ``GAPI_API_ROOT`` is no longer required, it defaults to
    ``"https://rest.gadventures.com"``

    * ``GAPI_APPLICATION_KEY`` is now required

    * ``GAPI_WEBHOOKS_VALIDATION_KEY`` is no longer used at all (we compute this
    value from your application key)

0.3.0 (2016-09-15)
------------------
* Raise exceptions in ``clean_events`` instead of returning them (the caller is
  expecting a list of webhook events, not an exception)
* Updated README to explain required settings

0.2.0 (2016-03-14)
------------------
* Do not reject webhook events whose ``data.href`` contain an id *and* a
  variation id (to accommodate ``itineraries`` resources)

v0.1.0 (2015-02-23)
-------------------
* First tagged release
