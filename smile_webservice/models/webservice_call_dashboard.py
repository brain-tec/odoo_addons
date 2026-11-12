# (C) 2021 Smile (<http://www.smile.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
import json
from collections import defaultdict
from datetime import datetime, time, timedelta

import pytz
from odoo.tools.misc import format_date, get_lang

from odoo import _, api, fields, models, tools

DASHBOARD_WEEKS = 12


class WebserviceCallDashboard(models.Model):
    """ One kanban card per webservice type, built from the existing calls """
    _name = 'webservice.call.dashboard'
    _description = 'Webservice calls dashboard'
    _auto = False
    _order = 'webservice_type'

    webservice_type = fields.Selection(selection='_selection_webservice_type', string='Webservice type',
                                       readonly=True)
    name = fields.Char(compute='_compute_dashboard')
    count_total = fields.Integer(string='Calls', compute='_compute_dashboard')
    count_error = fields.Integer(string='Errors', compute='_compute_dashboard')
    count_pending = fields.Integer(string='Pending', compute='_compute_dashboard')
    count_week = fields.Integer(string='Calls this week', compute='_compute_dashboard')
    count_week_error = fields.Integer(string='Errors this week', compute='_compute_dashboard')
    last_call_date = fields.Datetime(string='Last call', compute='_compute_dashboard')
    graph_data = fields.Text(compute='_compute_dashboard')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT ROW_NUMBER() OVER (ORDER BY webservice_type) AS id, webservice_type
                FROM webservice_call
                GROUP BY webservice_type
            )
        """)

    @api.model
    def _selection_webservice_type(self):
        return self.env['webservice.call']._fields['webservice_type']._description_selection(self.env)

    @api.model
    def _current_week_start(self):
        """ First day of the current week, following the user language (as the read_group week granularity) """
        today = fields.Date.context_today(self)
        first_week_day = int(get_lang(self.env).week_start) - 1
        return today - timedelta(days=(today.weekday() - first_week_day) % 7)

    @api.model
    def _to_utc_datetime(self, day):
        tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        return tz.localize(datetime.combine(day, time.min)).astimezone(pytz.utc).replace(tzinfo=None)

    def _type_domain(self):
        self.ensure_one()
        return [('webservice_type', '=', self.webservice_type)]

    def _compute_dashboard(self):
        Call = self.env['webservice.call']
        types = self.mapped('webservice_type')
        type_domain = [('webservice_type', 'in', [t for t in types if t])]
        if False in types:
            type_domain = ['|', ('webservice_type', '=', False)] + type_domain

        counts = defaultdict(lambda: defaultdict(int))
        last_dates = {}
        for ws_type, state, count, last_date in Call._read_group(
                type_domain, ['webservice_type', 'state'], ['__count', 'create_date:max']):
            counts[ws_type][state] = count
            last_dates[ws_type] = max(filter(None, [last_dates.get(ws_type), last_date]), default=False)

        current_week = self._current_week_start()
        weeks = [current_week - timedelta(weeks=i) for i in reversed(range(DASHBOARD_WEEKS))]
        weekly = defaultdict(lambda: defaultdict(lambda: {'total': 0, 'error': 0}))
        for ws_type, week, state, count in Call._read_group(
                type_domain + [('create_date', '>=', self._to_utc_datetime(weeks[0]))],
                ['webservice_type', 'create_date:week', 'state'], ['__count']):
            week = week.date()
            weekly[ws_type][week]['total'] += count
            if state == 'error':
                weekly[ws_type][week]['error'] += count

        type_labels = dict(self._fields['webservice_type']._description_selection(self.env))
        for dashboard in self:
            ws_type = dashboard.webservice_type
            type_counts = counts[ws_type]
            type_weekly = weekly[ws_type]
            dashboard.name = type_labels.get(ws_type) or _('Undefined')
            dashboard.count_total = sum(type_counts.values())
            dashboard.count_error = type_counts['error']
            dashboard.count_pending = type_counts['draft'] + type_counts['in_progress']
            dashboard.count_week = type_weekly[current_week]['total']
            dashboard.count_week_error = type_weekly[current_week]['error']
            dashboard.last_call_date = last_dates.get(ws_type, False)
            dashboard.graph_data = json.dumps({
                'labels': [format_date(self.env, week, date_format='dd MMM') for week in weeks],
                'calls': [type_weekly[week]['total'] for week in weeks],
                'errors': [type_weekly[week]['error'] for week in weeks],
                'calls_label': _('Calls'),
                'errors_label': _('Errors'),
            })

    def _action_open_calls(self, name, domain=None, context=None):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('smile_webservice.action_webservice_call_view')
        action_name = f'{self.name} - {name}'
        action.update({
            'name': action_name,
            'display_name': action_name,
            'domain': self._type_domain() + (domain or []),
            'context': context or {},
        })
        return action

    def action_open_calls(self):
        return self._action_open_calls(_('Calls'))

    def action_open_errors(self):
        return self._action_open_calls(_('Errors'), [('state', '=', 'error')])

    def action_open_week_errors(self):
        week_start = self._to_utc_datetime(self._current_week_start())
        return self._action_open_calls(_('Errors this week'),
                                       [('state', '=', 'error'), ('create_date', '>=', week_start)])

    def action_open_pending(self):
        return self._action_open_calls(_('Pending'), [('state', 'in', ('draft', 'in_progress'))])
