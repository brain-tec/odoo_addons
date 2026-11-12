import json
from datetime import timedelta

from odoo.tests.common import TransactionCase

from odoo import fields


class TestWebserviceCallDashboard(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['webservice.call'].search([]).unlink()
        cls.env['webservice.call'].create([
            {'name': 'ok', 'state': 'done'},
            {'name': 'ko', 'state': 'error'},
            {'name': 'draft', 'state': 'draft'},
        ])
        old_error = cls.env['webservice.call'].create({'name': 'old ko', 'state': 'error'})
        old_date = fields.Datetime.now() - timedelta(weeks=3)
        cls.env.cr.execute("UPDATE webservice_call SET create_date = %s WHERE id = %s", (old_date, old_error.id))
        old_error.invalidate_recordset(['create_date'])
        cls.dashboard = cls.env['webservice.call.dashboard'].search([('webservice_type', '=', False)])

    def test_counters(self):
        self.assertEqual(len(self.dashboard), 1)
        self.assertEqual(self.dashboard.count_total, 4)
        self.assertEqual(self.dashboard.count_error, 2)
        self.assertEqual(self.dashboard.count_pending, 1)
        self.assertEqual(self.dashboard.count_week, 3)
        self.assertEqual(self.dashboard.count_week_error, 1)

    def test_weekly_graph(self):
        data = json.loads(self.dashboard.graph_data)
        self.assertEqual(len(data['labels']), 12)
        self.assertEqual(data['calls'][-1], 3)
        self.assertEqual(data['errors'][-1], 1)
        self.assertEqual(data['errors'][-4], 1)
        self.assertEqual(sum(data['calls']), 4)

    def test_open_errors(self):
        action = self.dashboard.action_open_errors()
        self.assertEqual(self.env['webservice.call'].search_count(action['domain']), 2)
        action = self.dashboard.action_open_week_errors()
        self.assertEqual(self.env['webservice.call'].search_count(action['domain']), 1)
