# -*- coding: utf-8 -*-
# (C) 2024 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import passlib
import logging

from odoo import _, fields, models
from odoo.exceptions import AccessDenied

_logger = logging.getLogger(__name__)


class CasToken(models.Model):
    _name = 'cas.token'

    user_id = fields.Many2one('res.users')
    token = fields.Char()

    def create_token(self, user_id, token):
        res = self.create(
            {
                'user_id': user_id.id,
                'token': token,
            }
        )
        self.env.cr.commit()
        return res


class ResUsers(models.Model):
    _inherit = 'res.users'

    user_cas_id = fields.Char('User CAS id')

    def _get_cas_parameter_id(self):
        return self.env['cas.parameter'].search([], limit=1)

    def _check_credentials(self, password, env):
        """Override to handle CAS authentication.

        The token can be a password if the user has used the normal form...
        but we are more interested in the case when they are tokens
        and the interesting code is inside the "except" clause.
        """
        try:
            # Attempt a regular login (via other auth addons) first.
            return super()._check_credentials(password, env)

        except (AccessDenied, passlib.exc.PasswordSizeError):
            token = (
                self.env["cas.token"]
                .sudo()
                .search(
                    [
                        ("user_id", "=", self.env.user.id),
                        ("token", "=", password),
                    ]
                )
            )
            if not token:
                raise AccessDenied()
            return True

    def _cas_create_user(self):
        return self._get_cas_parameter_id().create_user_if_non_exists

    def _cas_update_user(self):
        return self._get_cas_parameter_id().update_user_attributes

    def _prepare_attribute_values(self, attributes):
        """
        params
            - attributes (type dict): CAS dict attributes,
                key is the cas name attribute
        Update attributes dict to set mapped fields in attributes_mapping_ids
        """
        cas_parameter = self._get_cas_parameter_id()
        linked_mappings = cas_parameter.attributes_mapping_ids
        cas_values = {}
        if attributes:
            for key, value in attributes.items():
                matching_mappings = linked_mappings.filtered(
                    lambda m: m.name == key)
                if matching_mappings:
                    for matching_mapping in matching_mappings:
                        cas_values[matching_mapping.field_name] = value
        return cas_values

    def _get_cas_matching_attribute(self):
        return self._get_cas_parameter_id().matching_attribute or 'user_cas_id'

    def _search_user(self, cas_user_id):
        matching_field = self._get_cas_matching_attribute()
        return self.with_context(active_test=False).search(
            [(matching_field, '=', cas_user_id)], limit=1)

    def _create_cas_user(self, attributes):
        auto_create = self._cas_create_user()
        user_id = self.browse()
        if not attributes or not auto_create:
            return user_id
        values = self._prepare_attribute_values(attributes)
        try:
            self.check_values(values)
        except ValueError as e:
            self.create_cas_user_error(e)
        if self.sudo().search([("login", "=", values.get("login"))]):
            raise ValueError(_(
                _('Another user is already registered using this login.')))

        try:
            user_id = self.sudo().with_context(no_reset_password=True).create(
                values
                )
        except Exception as e:
            _logger.error('Fail during CAS user creation ' + str(e))
        return user_id

    def _update_cas_user(self, attributes):
        if self._cas_update_user():
            values = self._prepare_attribute_values(attributes)
            self.write(values)
            self.env.cr.commit()

    def _get_or_create_cas_user(self, cas_id, attributes=None):
        """
            Look for existing res_users
                using configured field (matching_attribute)
            If no user found and parameter create_user_if_non_exists is True,
                res_user is created with CAS attributes values
            IF user is found and update_user_attributes is True
                in CAS parameters, user is updated with CAS attributes values

            @params :
                cas_id (str): used to find user in database
                attributes (dict) [Optional] : CAS attribute values to update
                    or create res_users fields

            @return :
                user_id (record)
        """

        user_id = self._search_user(cas_id)
        if not user_id:
            user_id = self._create_cas_user(attributes)
        else:
            user_id._update_cas_user(attributes)
        return user_id

    def check_values(self, values):
        mappings = self._get_cas_parameter_id().attributes_mapping_ids.filtered(
            lambda r: r.creation_requirement
        )
        if mappings:
            complete_values = all(
                field in values.keys() 
                    for field in mappings.mapped('field_name')
                                )
            if not complete_values:
                missing_fields = list(
                    set(
                        mappings.mapped('field_name')) - set(values.keys()
                        )
                    )
                raise ValueError(
                    _('Some fields are missing for user creation : %s') 
                        % ','.join(missing_fields))

    def create_cas_user_error(self, exception):
        raise ValueError(
            _('Error append during user creation: %s ') % exception
            )
