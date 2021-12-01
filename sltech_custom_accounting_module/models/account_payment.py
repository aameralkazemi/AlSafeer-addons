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
from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError

class AccountPayment(models.Model):
    _inherit = "account.payment"

    sltech_move_line_payment = fields.Boolean(default=False)
    sltech_move_id = fields.Many2one('account.move')

    def _prepare_payment_moves(self):
        res = super(AccountPayment, self)._prepare_payment_moves()

        if self._context.get('sltech_payment_bill'):
            for line in res[0]['line_ids']:
                line[2]['sltech_move_id'] = self._context.get('sltech_move_id').id

        return res

    def post(self):

        if self.sltech_move_line_payment:

            sltech_move_id = self.sltech_move_id

            # full line partial payment
            for line in sltech_move_id.sltech_move_line:

                for rec in line.payment_id:
                    moves = line.partial_payment_move_ids


                    # Update the state / move before performing any reconciliation.
                    move_name = self._get_move_name_transfer_separator().join(moves.mapped('name'))
                    rec.write({'state': 'posted', 'move_name': move_name})

                    if rec.payment_type in ('inbound', 'outbound'):
                        # ==== 'inbound' / 'outbound' ====
                        if rec.invoice_ids:
                            (moves[0] + rec.invoice_ids).line_ids \
                                .filtered(
                                lambda line: not line.reconciled and line.account_id == rec.destination_account_id) \
                                .reconcile()
                    elif rec.payment_type == 'transfer':
                        # ==== 'transfer' ====
                        moves.mapped('line_ids') \
                            .filtered(lambda line: line.account_id == rec.company_id.transfer_account_id) \
                            .reconcile()

            return True
            # end

        res = super(AccountPayment, self).post()


        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconcilable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconcilable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """

        return res