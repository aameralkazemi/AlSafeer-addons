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
from odoo.tools import date_utils
from odoo.tools.misc import format_date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
import json
import base64

class AccountMove(models.Model):
    _inherit = "account.move"

    is_tax_closing = fields.Boolean(help="technical field used to know if this move is the vat closing move", default=False)
    tax_report_control_error = fields.Boolean(help="technical field used to know if there was a failed control check")

    def action_open_tax_report(self):
        action = self.env.ref('account_reports.action_account_report_gt').read()[0]
        options = self._compute_vat_period_date()
        # Pass options in context and set ignore_session: read to prevent reading previous options
        action.update({'options': options, 'ignore_session': 'read'})
        return action

    def refresh_tax_entry(self):
        for move in self.filtered(lambda m: m.is_tax_closing and m.state == 'draft'):
            options = move._compute_vat_period_date()
            ctx = move.env['account.report']._set_context(options)
            ctx['strict_range'] = True
            move.env['account.generic.tax.report'].with_context(ctx)._generate_tax_closing_entry(options, move=move, raise_on_empty=True)

    def _compute_vat_period_date(self):
        self.ensure_one()
        date_to = self.date
        # Take the periodicity of tax report (1 or 3 months) from the company and since we base ourselve on the move
        # date as ending date for the period, we need to remove 0 or 2 month from that date and take the 1st of the month
        # to compute the starting period date.
        delay = self.company_id.account_tax_next_activity_type.delay_count - 1
        date_from = date_utils.start_of(date_to + relativedelta(months=-delay), 'month')
        options = {'date': {'date_from': date_from, 'date_to': date_to, 'filter': 'custom'}}
        report = self.env['account.generic.tax.report']
        return report._get_options(options)

    def _close_tax_entry(self):
        # Close the activity if any and create a new move and a new activity
        # also freeze lock date
        # and fetch pdf
        for move in self:
            # Check that date correspond to ending date of period.
            tax_activity_type = move.company_id.account_tax_next_activity_type or False
            periodicity = tax_activity_type.delay_count == 1 and 'month' or 'quarter'
            if move.date != date_utils.end_of(move.date, periodicity):
                raise UserError(_("Can't post the move with reference %s as its ending date %s does not correspond to end date of the period.") % (move.ref, move.date))
            activity = move.activity_ids.filtered(lambda m: m.activity_type_id == tax_activity_type)
            # Change lock date to date of the move
            move.company_id.tax_lock_date = move.date
            # Add pdf report as attachment to move
            options = move._compute_vat_period_date()
            ctx = self.env['account.report']._set_context(options)
            ctx['strict_range'] = True
            attachments = self.env['account.generic.tax.report'].with_context(ctx)._get_vat_report_attachments(options)
            # end activity
            if len(activity):
                activity.action_done()
            # post the message with the PDF
            subject = _('Vat closing from %s to %s') % (format_date(self.env, options.get('date').get('date_from')), format_date(self.env, options.get('date').get('date_to')))
            move.with_context(no_new_invoice=True).message_post(body=move.ref, subject=subject, attachments=attachments)
            # create the recurring entry (new draft move and new activity)
            next_date_deadline = move.date + relativedelta(day=move.company_id.account_tax_periodicity_reminder_day, months=move.company_id.account_tax_next_activity_type.delay_count + 1)
            vals = {
                'company_id': move.company_id,
                'account_tax_periodicity': move.company_id.account_tax_periodicity,
                'account_tax_periodicity_journal_id': move.company_id.account_tax_periodicity_journal_id,
                'account_tax_periodicity_next_deadline': next_date_deadline,
            }
            self.env['res.config.settings']._create_edit_tax_reminder(vals)

    def post(self):
        # When posting entry, generate the pdf and next activity for the tax moves.
        tax_return_moves = self.filtered(lambda m: m.is_tax_closing)
        tax_return_moves._close_tax_entry()
        return super(AccountMove, self).post()


class AccountTaxReportActivityType(models.Model):
    _inherit = "mail.activity.type"

    category = fields.Selection(selection_add=[('tax_report', 'Tax report')])

class AccountTaxReportActivity(models.Model):
    _inherit = "mail.activity"

    def action_open_tax_report(self):
        self.ensure_one()
        move = self.env['account.move'].browse(self.res_id)
        return move.action_open_tax_report()
