# -*- coding: utf-8 -*-
# (C) 2024 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, _):
    """
    Set ircp
    """
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        env['ir.config_parameter'].set_param('auth.cas', '1')
