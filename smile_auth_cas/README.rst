.. |badge1| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

.. |badge2| image:: https://img.shields.io/badge/github-Smile--SA%2Fodoo_addons-lightgray.png?logo=github
    :target: https://github.com/Smile-SA/odoo_addons/tree/13.0/smile_auth_cas
    :alt: Smile-SA/odoo_addons

|badge1| |badge2|

================
Smile Auth CAS
================

This module delegate authentication to a CAS server using CAS protocol.
https://apereo.github.io/cas/6.5.x/protocol/CAS-Protocol.html

**Table of contents**

.. contents::
   :local:


Requirements
============

This module require python-cas package
The code from https://github.com/python-cas/python-cas is used to parse
CAS protocol.


Usage
=====

Configuration
-------------

Activate or deactivate CAS authentication
^^^^^^^^^^^^^^^^^^^^^

Two parameters can be used to use or not CAS authentication :

- System parameter `auth.cas` (default '1')
- Configuration file `auth_cas` (default not present)

You can deactivate CAS authentication by just adding 
`auth_cas = False` in your .conf file

Or set the config_parameter `auth.cas` to '0'


Configure the version CAS server
^^^^^^^^^^^^^^^^^^^^^

Specify :

* the CAS server URL (for example https://cas.dmeo.fr/test/login)
* your service URL, the CAS will redirect to it after login (for example https://your_odoo/web/login)
* CAS version (3 is default, see https://apereo.github.io/cas/6.5.x/protocol/CAS-Protocol.html#303)
* if you want the CAS to update some user attributes at login
* which attributes are updated at login, by providing a mapping (CAS attribute name -> ODOO res_users field)
* if you want a user to be created on the fly if not exists on Odoo
* the mathing attribute to map the CAS user with Odoo user (default user_cas_id)

How does it work
^^^^^^^^^^^^^^^^^^^^^

At install, system parameter `auth.cas` is set to 1. Meaning that the CAS authentication will be activated.

* Protocol details:

This module override web_login and logout routes. 

At login, if user session is not active, and if there is not ST (service ticket),
a all to CAS server is made to get a ticket and the user is send to CAS login page.
Then the user is redirected back to Odoo, this time with a ST. 
The ST is validated by Odoo.

All of this is standard CAS login protocol.

* Authenticate on Odoo:

Assuming that user is authenticated on the CAS, and the ST is valdated,
the user is now technicly authenticated, but Odoo need to link the session with a res.user.

To do that, Odoo will use the uid given by the CAS during the precedent phase,
and search for an existing res_users with the egal field `user_cas_id` (or other custom confifured field).

To authenticate the user, we save the "token" from ticket created at login on CAS server, 
and link it with the founded (or created) user.

Then the _check_credentials is ovewritten to use this token instead of the classical password.

* Update or auto create new user:


- If the user attributes send by the CAS match with and existing res.users, the user is authenticated and some attributes can be updated (typically name, email ...)
based on the attributes configuration in cas.parameter model.
- If the user attributes send by the CAS match with and existing res.users but is not active,
the native authenticate method reject with and AccessDenied error.
- If no user match with the attributes send by the CAS, and if cas.parameter configured so, the user is created and authenticated.
(Some attributes may be flagged as required to create a user, like email)

It is important to known that, once the CAS authentication is activated,
the login is made by CAS for all users. 

The password authentication is still possible by xmlrpc.

Tips
^^^^^^^^^^^^^^^^^^^^^

A script (`/tools/tool_test_cas.py`) can help you to make some test,
by providing you and interractive menu to update logins, user_cas_id fields (and more) during tests with your CAS server.


Known Issues
============




Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/Smile-SA/odoo_addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/Smile-SA/odoo_addons/issues/new?body=module:%20smile_auth_cas%0Aversion:%213.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.


Credits
=======

Contributors
------------

* Martin Deconinck
* Joël MAUBREY

Maintainer
----------

This module is maintained by Smile SA.

Since 1991 Smile has been a pioneer of technology and also the European expert in open source solutions.
