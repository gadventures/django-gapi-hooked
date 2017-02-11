.. :changelog:

History
=======

Unreleased (master branch)
--------------------------
* Add MIT License, begin preparing ``setup.py`` for a release on PyPI
* Add resource-name-based dynamic dispatch to ``WebhookReceiverView`` (e.g you
  can define a ``handle_profiles`` method on your subclass and it will handle
  ``profiles`` events without having to write your own routing code, see README
  for examples)
* Add a (presently very small) test suite
* ``GAPI_API_ROOT`` is no longer a required setting, it now defaults to
  ``"https://rest.gadventures.com"``

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
