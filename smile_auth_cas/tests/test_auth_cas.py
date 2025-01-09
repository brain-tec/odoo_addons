# Copyright 2024 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from unittest import mock
from werkzeug.urls import url_parse

from odoo.tests import common, tagged
from odoo.addons.smile_auth_cas.tests.auth_cas_common import AuthCasCommon
from odoo.http import request
from odoo import sql_db
ADMIN_USER_ID = common.ADMIN_USER_ID


@tagged('post_install', '-at_install')
@mock.patch("odoo.http.Request.validate_csrf", return_value=True)
@mock.patch("odoo.addons.smile_auth_cas.controllers.main.CASLogin._cas_authenticate", return_value=True)
class TestLoginCAS(AuthCasCommon):
    def setUp(self):
        super(TestLoginCAS, self).setUp()

    def test_01_web_login_failed(self, *args):
        """
            CAS return a valid ticket but no related user found in Odoo
        """
        with mock.patch(self.CASLogin + '._cas_verify_ticket') \
                as _mock_verify:
            _mock_verify.return_value = [
                    '01234',
                    {
                    'uid': '01234',
                    'firstname': 'Felix',
                    'lastname': 'Angel',
                    },
                    ''
            ]
            res = self.url_open("/web/login",
            {'ticket': 'ST-9999-AbCfF12321-cas-test',}
            )
            path = url_parse(res.url).path
            self.assertIn('/cas_error', path)
            self.assertEqual(res.status_code, 200)

    def test_02_web_login_success(self, *args):
        """
            Assume that CAS server auth was successful
            And an user exists with cas_user_id given by _cas_verify_ticket

            Expect successful login
        """
        with mock.patch(self.CASLogin + '._cas_verify_ticket') \
                as _mock_verify:
            _mock_verify.return_value = [
                    '01234',
                    {
                    'uid': '01234', 
                    'firstname': 'Felix', 
                    'lastname': 'Angel',
                    },
                    ''
            ]
            with mock.patch('odoo.addons.smile_auth_cas.models.res_users.ResUsers._search_user') as _mock_get_cas_user:
                _mock_get_cas_user.return_value = self.admin_user_id
                res = self.url_open("/web/login", 
                {'ticket': 'ST-9999-AbCfF12321-cas-test',}
                )
                path = url_parse(res.url).path
                self.assertEqual(res.status_code, 200)
                self.assertEqual(path, '/web')

    def test_03_web_auto_create_user(self, *args):
        """
            Assume that CAS server auth was successful
            And an user NOT exists with cas_user_id given by _cas_verify_ticket
            _mock_create_user parameter return True

            Expect user to be created and successful login
        """

        user_id = self.env['res.users'].search([('login', '=', 'felix')])
        self.assertEqual(len(user_id), 0)
        with mock.patch(self.CASLogin + '._cas_verify_ticket') \
                as _mock_verify:
            _mock_verify.return_value = [
                    '01234',
                    {
                    'user_cas_id': '01234',
                    'login': 'felix',
                    'name': 'Angel',
                    },
                    ''
            ]
            with mock.patch('odoo.addons.smile_auth_cas.models.res_users.ResUsers._cas_create_user') as _mock_create_user:
                _mock_create_user.return_value = True
                res = self.url_open("/web/login", 
                {'ticket': 'ST-9999-AbCfF12321-cas-test',}
                )
                self.assertEqual(res.status_code, 200)

            user_id = self.env['res.users'].sudo().search([('login', '=', 'felix'), ('user_cas_id', '=', '01234')])
            self.assertEqual(len(user_id), 1)

    def test_04_web_login_update(self, *args):
        """
            Assume that CAS server auth was successful
            And an user exists with cas_user_id given by _cas_verify_ticket

            Expect successful login and user fields updated
        """
        with mock.patch.object(sql_db.Cursor, "commit", self.mock_commit):
            self.assertNotEqual(self.admin_user_id.name, 'new_name')
            with mock.patch(self.CASLogin + '._cas_verify_ticket') \
                    as _mock_verify:
                _mock_verify.return_value = [
                        '01234',
                        {
                        'name': 'new_name',
                        },
                        ''
                ]
                with mock.patch('odoo.addons.smile_auth_cas.models.res_users.ResUsers._search_user') as _mock_get_cas_user:
                    _mock_get_cas_user.return_value = self.admin_user_id
                    with mock.patch('odoo.addons.smile_auth_cas.models.res_users.ResUsers._cas_update_user') as _mock_update_user:
                        _mock_update_user.return_value = True
                        res = self.url_open("/web/login",
                        {'ticket': 'ST-9999-AbCfF12321-cas-test',}
                        )
                        path = url_parse(res.url).path
                        self.assertEqual(res.status_code, 200)
                        self.assertEqual(path, '/web')
                        self.assertEqual(self.admin_user_id.name, 'new_name')

    def test_05_web_auto_create_user_error(self, *args):
        """
            Assume that CAS server auth was successful
            And an user NOT exists with cas_user_id given by _cas_verify_ticket
            _mock_create_user parameter return True
            And we have missing attributes from the CAS, that does not permit
            user creation

            Expect user NOT to be created
        """

        self.env['attributes.mapping'].create(
            {'name': 'req_attr',
            'field_name': 'email',
            'creation_requirement': True,
            'cas_parameter_id': self.param1.id}
        )
        user_id = self.env['res.users'].search([('login', '=', 'felix')])
        self.assertEqual(len(user_id), 0)
        with mock.patch(self.CASLogin + '._cas_verify_ticket') \
                as _mock_verify:
            _mock_verify.return_value = [
                    '01234',
                    {
                    'user_cas_id': '01234',
                    'login': 'felix',
                    'name': 'Angel',
                    'password': 'felix',
                    },
                    ''
            ]
            with mock.patch('odoo.addons.smile_auth_cas.models.res_users.ResUsers._cas_create_user') as _mock_create_user:
                _mock_create_user.return_value = True
                res = self.url_open("/web/login",
                {'ticket': 'ST-9999-AbCfF12321-cas-test',}
                )
                self.assertEqual(res.status_code, 200)

            user_id = self.env['res.users'].search([('login', '=', 'felix')])
            self.assertEqual(len(user_id), 0)
