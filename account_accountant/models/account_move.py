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
from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'account.move')], string='Attachments')


class AccountPayment(models.Model):
    _inherit = "account.payment"

    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'account.payment')], string='Attachments')


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'account.bank.statement')], string='Attachments')


class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = "account.move.line"

    move_attachment_ids = fields.One2many('ir.attachment', compute='_compute_attachment')

    @api.depends('move_id', 'payment_id')
    def _compute_attachment(self):
        for record in self:
            record.move_attachment_ids = record.move_id.attachment_ids + record.statement_id.attachment_ids + record.payment_id.attachment_ids
