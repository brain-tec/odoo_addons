
# -*- coding: utf-8 -*-
# (C) 2024 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


{
    "name": "Smile CAS Authentication",
    "version": "16.0.0",
    "category": "Tools",
    "author": "Smile",
    "license": "AGPL-3",
    "description": "Delegate authentication to a CAS",
    "depends": ["web",
                "auth_oauth"],
    "demo": [],
    "data": [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/attributes_mapping.xml',
        'views/res_users_views.xml',
        'views/cas_parameter_views.xml',
        'views/menu.xml',
    ],
    "installable": True,
    "auto_install": False,
    "post_init_hook": "post_init_hook",
    'external_dependencies': {
        'python': ['python-cas'],
    }
}
