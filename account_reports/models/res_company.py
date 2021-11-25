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
from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    totals_below_sections = fields.Boolean(
        string='Add totals below sections',
        help='When ticked, totals and subtotals appear below the sections of the report.')
    account_tax_periodicity = fields.Selection([
        ('trimester', 'trimester'),
        ('monthly', 'monthly')], string="Delay units", help="Periodicity", default='monthly')
    account_tax_periodicity_reminder_day = fields.Integer(string='Start from', default=7)
    account_tax_original_periodicity_reminder_day = fields.Integer(string='Start from original', help='technical helper to prevent rewriting activity date when saving settings')
    account_tax_periodicity_journal_id = fields.Many2one('account.journal', string='Journal', domain=[('type', '=', 'general')])
    account_tax_next_activity_type = fields.Many2one('mail.activity.type')

    def _get_default_misc_journal(self):
        """ Returns a default 'miscellanous' journal to use for
        account_tax_periodicity_journal_id field. This is useful in case a
        CoA was already installed on the company at the time the module
        is installed, so that the field is set automatically when added."""
        return self.env['account.journal'].search([('type', '=', 'general'), ('show_on_dashboard', '=', True), ('company_id', '=', self.id)], limit=1)

    def write(self, values):
        # in case the user want to change the journal or the periodicity without changing the date, we should change the next_activity
        # therefore we set the account_tax_original_periodicity_reminder_day to false so that it will be recomputed
        for company in self:
            if (values.get('account_tax_periodicity', company.account_tax_periodicity) != company.account_tax_periodicity \
            or values.get('account_tax_periodicity_journal_id', company.account_tax_periodicity_journal_id.id) != company.account_tax_periodicity_journal_id.id):
                values['account_tax_original_periodicity_reminder_day'] = False
        return super(ResCompany, self).write(values)
