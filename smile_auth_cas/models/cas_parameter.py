# -*- coding: utf-8 -*-
# (C) 2024 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CasParameter(models.Model):
    _name = 'cas.parameter'
    _rec_name = 'cas_server_url'
    _description = 'Cas parameter'

    def default_cas_service_url(self):
        web_base_url = self.env['ir.config_parameter'].\
            get_param('web.base.url')
        return web_base_url + 'web/login'\
            if web_base_url.endswith('/') \
            else web_base_url + '/web/login'

    active = fields.Boolean()
    cas_server_url = fields.Char(string='CAS server URL', required=True)
    cas_service_url = fields.Char(string='Service URL', required=True, 
                default=lambda self: self.default_cas_service_url())
    cas_version = fields.Char(default='3', required=True)
    update_user_attributes = fields.Boolean(
        string='Update user attributes',
        help='Allow to define if attributes (name, firstname) gived by CAS \
            to login have to update Odoo datas'
    )
    create_user_if_non_exists = fields.Boolean(
        string='Create user if non exists')
    attributes_mapping_ids = fields.One2many('attributes.mapping', 
                                             'cas_parameter_id')
    matching_attribute = fields.Char(default='user_cas_id', required=True)

    @api.constrains('active')
    def _check_matching_attribute(self):
        active_cas = self.search([('active', '=', True)])
        if len(active_cas) > 1:
            raise ValidationError(_('Only one cas parameter can be active'))
