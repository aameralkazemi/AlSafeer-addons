# -*- coding: utf-8 -*-
##############################################################################
#
#    SLTECH ERP SOLUTION
#    Copyright (C) 2020-Today(www.slecherpsolution.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import fields, models, _
from odoo.exceptions import AccessError


class Digest(models.Model):
    _inherit = 'digest.digest'

    kpi_account_bank_cash = fields.Boolean('Bank & Cash Moves')
    kpi_account_bank_cash_value = fields.Monetary(compute='_compute_kpi_account_total_bank_cash_value')

    def _compute_kpi_account_total_bank_cash_value(self):
        if not self.env.user.has_group('account.group_account_user'):
            raise AccessError(_("Do not have access, skip this data for user's digest email"))
        for record in self:
            start, end, company = record._get_kpi_compute_parameters()
            account_moves = self.env['account.move'].read_group([
                ('date', '>=', start),
                ('date', '<', end),
                ('journal_id.type', 'in', ['cash', 'bank']),
                ('company_id', '=', company.id)], ['journal_id', 'amount_total'], ['journal_id'])
            record.kpi_account_bank_cash_value = sum([account_move['amount_total'] for account_move in account_moves])

    def compute_kpis_actions(self, company, user):
        res = super(Digest, self).compute_kpis_actions(company, user)
        res.update({'kpi_account_bank_cash': 'account.open_account_journal_dashboard_kanban&menu_id=%s' % (self.env.ref('account.menu_finance').id)})
        return res
