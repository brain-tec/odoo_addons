# -*- coding: utf-8 -*-
# (C) 2022 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import werkzeug.utils

import odoo
from odoo.addons.web.controllers.session import (
    Session,
)
from odoo.addons.web.controllers.utils import ensure_db
from odoo.addons.auth_oauth.controllers.main import (
    OAuthLogin
)
from odoo import SUPERUSER_ID, _, api, http
from odoo.http import request
from odoo.tools.config import config

from cas import CASClient


_logger = logging.getLogger(__name__)


# ----------------------------------------------------------
# Controller
# ----------------------------------------------------------

class CASMixin(http.Controller):

    def _cas_authenticate(self):
        return request.env['ir.config_parameter'].sudo().get_param(
            'auth.cas') == '1' and config.get('auth_cas') != False

    def _get_cas_parameters(self):
        cas_parameter_id = request.env['cas.parameter'].sudo().search(
            [], limit=1)
        params = dict(
            version=cas_parameter_id.cas_version,
            server_url=cas_parameter_id.cas_server_url,
            service_url=cas_parameter_id.cas_service_url,
        )
        return params

    def _get_cas_client(self): 
        params = self._get_cas_parameters()
        cas_client = CASClient(
            version=params.get('version', 3),
            server_url=params.get('server_url', ''),
            service_url=params.get('service_url', ''),
        )
        return cas_client

    def _redirect_to_cas(self, url, code):
        redirect = werkzeug.utils.redirect(url, code)
        redirect.autocorrect_location_header = True
        return redirect

    def _get_cas_ticket(self):
        cas_client = self._get_cas_client()
        cas_login_url = cas_client.get_login_url()
        redirect = self._redirect_to_cas(cas_login_url, 303)
        return redirect

    def _cas_verify_ticket(self, ticket):
        cas_client = self._get_cas_client()
        return cas_client.verify_ticket(ticket)

    @http.route('/cas_error', auth='public')
    def cas_login_failed(self, **kw):
        return request.render('smile_auth_cas.login_error', {
            'message': kw.get('message')
        })

    def _logout_cas(self, redirect_url=None):
        cas_client = self._get_cas_client()
        url = cas_client.get_logout_url(redirect_url)
        redirect = werkzeug.utils.redirect(url, 303)
        redirect.autocorrect_location_header = True
        return redirect


class CASLogout(Session, CASMixin):

    @http.route()
    def logout(self, redirect='/web'):
        res = super(CASLogout, self).logout(redirect)
        new_redirect = self._logout_cas()
        res.location = new_redirect.location
        return res


class CASLogin(OAuthLogin, CASMixin):

    @http.route('/cas_error', auth='public')
    def cas_login_failed(self, **kw):
        return request.render('smile_auth_cas.login_error', {
            'message': kw.get('message')
        })

    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()
        request.is_frontend = True
        request.lang = request.env['res.lang'].search(
            [('code', '=', request.env.lang)])
        request.website = request.env['website'].get_current_website()
        if request.httprequest.method == 'GET' \
                and request.session.uid \
                and request.params.get('redirect'):
            # Redirect if already logged in and redirect param is present
            return request.redirect(request.params.get('redirect'))

        ticket = request.params.get('ticket')
        if kw.get('cas_error'):
            redirect = werkzeug.utils.redirect(
                '/cas_error?message=%s' % kw.get('cas_error'), 303)
            redirect.autocorrect_location_header = True
            return redirect
        from_cas_button = request.session.get('from_cas_button')
        if not from_cas_button:
            return super(CASLogin, self).web_login(*args, **kw)

        if not ticket:
            # No ticket, the request come from end user, send to CAS login
            redirect = self._get_cas_ticket()
            if redirect:
                return redirect

        cr = request.env.cr
        # There is a ticket, the request come from CAS as callback.
        # need call `verify_ticket()` to validate ticket and get user profile.
        user, attributes, _ = self._cas_verify_ticket(ticket)

        try:
            env = api.Environment(cr, SUPERUSER_ID, {})
            user_id = env['res.users'].sudo()._get_or_create_cas_user(
                user, attributes
                )
            if len(user_id) != 1 or not user:
                raise odoo.exceptions.AccessDenied()

            token_id = env['cas.token'].sudo().search(
                    [('user_id', '=', user_id.id)]
                )
            if token_id:
                token_id.token = ticket
                request.env.cr.commit()
            else:
                _logger.info("Creating cas_token")
                token_id = env['cas.token'].sudo().create_token(
                    user_id, ticket)
            uid = request.session.authenticate(
                request.session.db, user_id.login, ticket)
            request.params['login_success'] = True
            request.params['password'] = ticket
            return request.redirect(self._login_redirect(uid))
        except odoo.exceptions.AccessDenied:
            # cas credentials not valid,
            # user could be on a temporary session
            _logger.info("CAS: access denied")

            url = "/web/login?cas_error=access-denied"
            redirect = werkzeug.utils.redirect(url, 303)
            redirect.autocorrect_location_header = False
            return redirect

        except Exception as e:
            # signup error
            _logger.exception("CAS: failure - %s", str(e))
            url = "/web/login?cas_error=" + str(e)
            redirect = werkzeug.utils.redirect(url, 303)
            redirect.autocorrect_location_header = False
            return redirect
