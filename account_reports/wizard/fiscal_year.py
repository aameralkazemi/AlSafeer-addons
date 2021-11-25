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
from datetime import date

from odoo import _, api, fields, models


class FinancialYearOpeningWizard(models.TransientModel):
    _inherit = 'account.financial.year.op'
    _description = 'Opening Balance of Financial Year'

    account_tax_periodicity = fields.Selection(related='company_id.account_tax_periodicity', string='Periodicity', readonly=False, required=True)
    account_tax_periodicity_reminder_day = fields.Integer(related='company_id.account_tax_periodicity_reminder_day', string='Reminder', readonly=False, required=True)
    account_tax_periodicity_journal_id = fields.Many2one(related='company_id.account_tax_periodicity_journal_id', string='Journal', readonly=False)

    def write(self, vals):
        res = super().write(vals)
        if vals.get('account_tax_periodicity') or vals.get('account_tax_periodicity_reminder_day') or vals.get('account_tax_periodicity_journal_id'):
            self.env['res.config.settings']._update_account_tax_periodicity_reminder_day()

        return res
