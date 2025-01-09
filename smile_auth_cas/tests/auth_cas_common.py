# Copyright 2024 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from odoo.tests.common import HttpCase

from odoo.tests import tagged


@tagged('post_install', '-at_install')
class AuthCasCommon(HttpCase):
    def setUp(self):
        super(AuthCasCommon, self).setUp()
        self.env['cas.parameter'].search([]).write({'active': False})
        self.CAS_main = 'odoo.addons.smile_auth_cas.controllers.main'
        self.CASLogin = self.CAS_main + '.CASLogin'
        # self.base_url = self.env['ir.config_parameter'].get_param(
        #         'web.base.url')
        self.admin_user_id = self.env['res.users'].search(
            [('login', '=', 'admin')])
        mapping_ids = self.env['attributes.mapping'].browse()
        mapping_ids |= self.env['attributes.mapping'].create(
            {'name': 'login',
            'field_name': 'login'})
        mapping_ids |= self.env['attributes.mapping'].create(
            {'name': 'name',
            'field_name': 'name'}
        )
        mapping_ids |= self.env['attributes.mapping'].create(
            {'name': 'user_cas_id',
            'field_name': 'user_cas_id'}
        )
        self.param1 = self.env['cas.parameter'].create(
            {
                'active': True,
                'cas_version': '3',
                'cas_server_url': 'https://cas.test.com',
                'cas_service_url': 'https://odoo.test.com',
                'attributes_mapping_ids': [(6, 0, mapping_ids.ids)],
            }
        )
