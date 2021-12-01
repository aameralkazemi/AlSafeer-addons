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

class AccountInvoice(models.Model):
    _inherit = "account.move"

    # sltech_product_ids = fields.Many2many('product.product', string="Third Party Vendors", domain="[('additional_info', '=', True)]")
    sltech_move_line = fields.One2many('sltech.account.move.line', 'sltech_move_id', string="Third Party Vendors")
    sltech_price_subtotal = fields.Float('Price Total')

    sltech_amount_untaxed = fields.Float(compute='_sltech_compute_all', store=True, string='Amount Untaxed')
    sltech_amount_by_group = fields.Binary()
    sltech_amount_total = fields.Float(compute='_sltech_compute_all', store=True, string='Amount Total')
    sltech_invoice_payments_widget = fields.Text()
    sltech_amount_residual = fields.Float(compute='_sltech_compute_all', store=True, string='Amount Residual')
    sltech_invoice_outstanding_credits_debits_widget = fields.Text()

    sltech_move_line_entries = fields.One2many('account.move.line', 'sltech_move_id')

    @api.depends('line_ids', 'line_ids.is_landed_costs_line', 'sltech_move_line')
    def _compute_landed_costs_visible(self):
        for account_move in self:
            if account_move.landed_costs_ids:
                account_move.landed_costs_visible = False
            else:
                account_move.landed_costs_visible = any(line.is_landed_costs_line for line in account_move.line_ids)

            if account_move.sltech_move_line:
                account_move.landed_costs_visible = True



    def button_create_landed_costs(self):
        """Create a `stock.landed.cost` record associated to the account move of `self`, each
        `stock.landed.costs` lines mirroring the current `account.move.line` of self.
        """
        self.ensure_one()
        cost_lines = []
        landed_costs_lines = self.line_ids.filtered(lambda line: line.is_landed_costs_line)
        if landed_costs_lines:
            for l in landed_costs_lines:
                cost_lines.append((0, 0, {
                    'product_id': l.product_id.id,
                    'name': l.product_id.name,
                    'account_id': l.product_id.product_tmpl_id.get_product_accounts()['stock_input'].id,
                    'price_unit': l.currency_id._convert(l.price_subtotal, l.company_currency_id, l.company_id, l.move_id.date),
                    'split_method': 'equal',
                }))

        sltech_landed_costs_lines = self.sltech_move_line   #.filtered(lambda line: line.is_landed_costs_line)
        if self.sltech_move_line:
            for l in sltech_landed_costs_lines:
                cost_lines.append((0, 0, {
                    'product_id': l.product_id.id,
                    'name': l.product_id.name,
                    'account_id': l.product_id.product_tmpl_id.get_product_accounts()['stock_input'].id,
                    'price_unit': self.env.user.company_id.currency_id._convert(l.price_subtotal, self.env.user.company_id.currency_id, self.env.user.company_id,
                                                         l.sltech_move_id.date),
                    'split_method': 'equal',
                }))

        landed_costs = self.env['stock.landed.cost'].create({
            'vendor_bill_id': self.id,
            'cost_lines': cost_lines,
        })
        action = self.env.ref('stock_landed_costs.action_stock_landed_cost').read()[0]
        return dict(action, view_mode='form', res_id=landed_costs.id, views=[(False, 'form')])


    @api.depends('sltech_move_line.product_id', 'sltech_move_line.quantity', 'sltech_move_line.price_unit', 'state', 'invoice_payment_state')
    def _sltech_compute_all(self):
        for rec in self:
            total = 0
            for line in rec.sltech_move_line:
                line.price_subtotal = line.price_unit * line.quantity
                total += line.price_subtotal
            rec.sltech_amount_total = total
            rec.sltech_amount_untaxed = 0
            # rec.sltech_amount_residual = sum(x.payment_id.amount for x in rec.sltech_move_line if x.payment_id.state == 'draft')

    # def write(self, vals):
    #     res = super(AccountInvoice, self).write(vals)
    #
    #     if self.invoice_payment_state == 'paid':
    #         for pro_id in self.sltech_product_ids:
    #             if pro_id.list_price != 0:
    #                 record_id = self.env['account.payment'].sudo()
    #                 default_values = record_id.default_get(record_id._fields.keys())
    #                 default_values.update({
    #                     'amount': pro_id.list_price,
    #                     # 'currency_id': post.get('currency_id'),
    #                     # 'payment_date': datetime.datetime.strptime(post.get('payment_date'), "%m/%d/%Y").strftime(
    #                     #     "%Y-%m-%d"),  # post.get('payment_date'),
    #                     'communication': self.name,
    #                     'journal_id': self.journal_id.id,
    #                     # 'expense_account_id': post.get('expense_account_id'),
    #                     # 'branch_id': post.get('branch_id'),
    #                     'partner_id': pro_id.seller_ids[0].name.id,
    #                     'payment_type': 'outbound',
    #                     'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id,
    #                 })
    #
    #                 record_id = record_id.create(default_values)
    #                 record_id.with_context(sltech_payment_bill='sltech_payment_bill', prod_id=pro_id).post()
    #
    #     return res

    def action_post(self):
        res = super(AccountInvoice, self).action_post()

        for line in self.sltech_move_line:
            record_id = self.env['account.payment']
            default_values = record_id.default_get(record_id._fields.keys())
            if not line.product_id.seller_ids:
                raise ValidationError('Please set vendor inside %s!'%line.product_id.name)
            default_values.update({
                'amount': line.price_subtotal,
                # 'currency_id': post.get('currency_id'),
                # 'payment_date': datetime.datetime.strptime(post.get('payment_date'), "%m/%d/%Y").strftime(
                #     "%Y-%m-%d"),  # post.get('payment_date'),
                'communication': self.name,
                'journal_id': self.journal_id.id,
                # 'expense_account_id': post.get('expense_account_id'),
                # 'branch_id': post.get('branch_id'),
                'partner_id': line.product_id.seller_ids[0].name.id,
                'payment_type': 'outbound',
                'partner_type': 'supplier',
                'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id,
            })

            record_id = record_id.create(default_values)
            record_id.with_context(sltech_payment_bill='sltech_payment_bill', prod_id=line.product_id, sltech_move_id=self.id)  #.post()

            # account_payment
            AccountMove = self.env['account.move'].with_context(default_type='entry')
            for rec in record_id:

                if rec.state != 'draft':
                    raise UserError(_("Only a draft payment can be posted."))

                if any(inv.state != 'posted' for inv in rec.invoice_ids):
                    raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

                # keep the name in case of a payment reset to draft
                if not rec.name:
                    # Use the right sequence to set the name
                    if rec.payment_type == 'transfer':
                        sequence_code = 'account.payment.transfer'
                    else:
                        if rec.partner_type == 'customer':
                            if rec.payment_type == 'inbound':
                                sequence_code = 'account.payment.customer.invoice'
                            if rec.payment_type == 'outbound':
                                sequence_code = 'account.payment.customer.refund'
                        if rec.partner_type == 'supplier':
                            if rec.payment_type == 'inbound':
                                sequence_code = 'account.payment.supplier.refund'
                            if rec.payment_type == 'outbound':
                                sequence_code = 'account.payment.supplier.invoice'
                    rec.name = self.env['ir.sequence'].next_by_code(sequence_code, sequence_date=rec.payment_date)
                    if not rec.name and rec.payment_type != 'transfer':
                        raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

                moves = AccountMove.create(rec.with_context(sltech_payment_bill='sltech_payment_bill', prod_id=line.product_id, sltech_move_id=self)._prepare_payment_moves())
                moves.filtered(lambda move: move.journal_id.post_at != 'bank_rec').post()

                # payment to third party by SL TECH ERP SOLUTION
                # if rec._context.get('sltech_payment_bill'):
                    # moves.name = rec.name
                product_id = line.product_id
                if [x for x in moves.line_ids if x.debit]:
                    tmp_ln_id = [x for x in moves.line_ids if x.debit][0]

                    fiscal_position = moves.fiscal_position_id
                    accounts = product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fiscal_position)
                    stock_input = None
                    if accounts['stock_input']:
                        stock_input = accounts['stock_input']

                    # tmp_ln_id.account_id = stock_input.id
                    tmp_ln_id.name = product_id.display_name
                    tmp_ln_id.product_id = product_id.id
                    # tmp_ln_id.move_id = self._context.get('sltech_move_id').id

                    # tmp_ln_id.journal_id = self.env.ref('tf_custom_module.sltech_money_out').id
                if [x for x in moves.line_ids if x.credit]:
                    tmp_ln_id = [x for x in moves.line_ids if x.credit][0]
                    tmp_ln_id.account_id = product_id.additional_account_id.id
                    # tmp_ln_id.move_id = self._context.get('sltech_move_id').id
                # end



                line.partial_payment_move_ids = [(6, 0, moves.ids)]

                line.payment_id = record_id.id
                line.payment_id.sltech_move_line_payment = True
                line.payment_id.sltech_move_id = self.id
            # end

        return res

class SLTECHAccountMoveLine(models.Model):
    _name = "sltech.account.move.line"

    sltech_move_id = fields.Many2one('account.move')
    product_id = fields.Many2one('product.product', domain="[('additional_info', '=', True), ('landed_cost_ok', '=', True)]")
    quantity = fields.Float("Quantity")
    name = fields.Char()
    debit = fields.Float('Debit')
    credit = fields.Float('Credit')
    account_id = fields.Many2one('account.account', 'Account')
    price_unit = fields.Float('Unit Price')
    price_subtotal = fields.Float('Subtotal', store=True)

    payment_id = fields.Many2one('account.payment', 'Payment')
    payment_state = fields.Selection(related='payment_id.state')

    partial_payment_move_ids = fields.Many2many('account.move')

    @api.onchange('product_id')
    def onchange_pro_id(self):
        if self.product_id:
            self.price_unit = self.product_id.list_price
            self.quantity = 1

            self.price_subtotal = self.price_unit * self.quantity

    @api.onchange('quantity', 'price_unit')
    def onchange_quantityprice_unit(self):
        self.price_subtotal = self.price_unit * self.quantity

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    sltech_move_id = fields.Many2one('account.move')