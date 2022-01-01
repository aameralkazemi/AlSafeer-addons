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
    sltech_amount_tax = fields.Float(compute='_sltech_compute_all', store=True, string='Amount Tax')
    sltech_amount_by_group = fields.Binary()
    sltech_amount_total = fields.Float(compute='_sltech_compute_all', store=True, string='Amount Total')
    sltech_invoice_payments_widget = fields.Text()
    sltech_amount_residual = fields.Float(compute='_sltech_compute_all', store=True, string='Amount Residual')
    sltech_invoice_outstanding_credits_debits_widget = fields.Text()

    sltech_move_line_entries = fields.One2many('account.move.line', 'sltech_move_id')

    sltech_move_id = fields.Many2one('account.move')  # to store third party move line entries   ====>   totally seperate and independent of other fields

    def sltech_button_create_landed_costs(self):
        """Create a `stock.landed.cost` record associated to the account move of `self`, each
                `stock.landed.costs` lines mirroring the current `account.move.line` of self.
                """
        if self.sltech_move_line:
            self.ensure_one()
            cost_lines = []
            landed_costs_lines = self.line_ids.filtered(lambda line: line.is_landed_costs_line)
            if landed_costs_lines:
                for l in landed_costs_lines:
                    cost_lines.append((0, 0, {
                        'product_id': l.product_id.id,
                        'name': l.product_id.name,
                        'account_id': l.product_id.product_tmpl_id.get_product_accounts()['stock_input'].id,
                        'price_unit': l.currency_id._convert(l.price_subtotal, l.company_currency_id, l.company_id,
                                                             l.move_id.date),
                        'split_method': 'equal',
                    }))

            sltech_landed_costs_lines = self.sltech_move_line  # .filtered(lambda line: line.is_landed_costs_line)
            if self.sltech_move_line:
                for l in sltech_landed_costs_lines:
                    cost_lines.append((0, 0, {
                        'product_id': l.product_id.id,
                        'name': l.product_id.name,
                        'account_id': l.product_id.product_tmpl_id.get_product_accounts()['stock_input'].id,
                        'price_unit': self.env.user.company_id.currency_id._convert(l.price_untax,
                                                                                    self.env.user.company_id.currency_id,
                                                                                    self.env.user.company_id,
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
            untax_total = 0
            tax_total = 0
            for line in rec.sltech_move_line:

                tax_details = line.tax_ids.compute_all(price_unit=line.price_unit, currency=False,
                                                       quantity=line.quantity, product=line.product_id)

                line.price_subtotal = tax_details['total_included']
                line.price_untax = tax_details['total_excluded']
                line.amount_tax = abs(tax_details['total_included'] - tax_details['total_excluded'])

                # line.price_subtotal = line.price_unit * line.quantity
                total += line.price_subtotal
                untax_total += tax_details['total_excluded']
                tax_total += abs(tax_details['total_included'] - tax_details['total_excluded'])
            rec.sltech_amount_total = total
            rec.sltech_amount_untaxed = untax_total
            rec.sltech_amount_tax = tax_total
            # rec.sltech_amount_residual = sum(x.payment_id.amount for x in rec.sltech_move_line if x.payment_id.state == 'draft')

    def sltech_action_post(self):
        if self.sltech_move_line:
            if not self.sltech_move_id:

                self.sltech_move_id = self.create({
                    'partner_id': self.partner_id.id,
                    'name': self.name+'-Landed Cost',
                    'date': self.date,
                    'journal_id': self.journal_id.id,
                    'currency_id': self.currency_id.id,
                }).id

            account_payable = self.env['account.account'].search(
                [
                    # ('user_type_id', '=', self.env.ref('account.data_account_type_payable').id),
                    ('name', '=', 'Account Payable'),
                    ('company_id', '=', self.company_id.id)], limit=1)

            line_ids = [(0, 0, {
                'account_id': line.product_id.additional_account_id.id,
                'name': line.product_id.name,
                'debit': line.price_untax,
                'sltech_move_id': self.id,
            }) for line in self.sltech_move_line] + [(0, 0, {
                'account_id': account_payable.id,
                'name': account_payable.name,
                'credit': self.sltech_amount_total,
                'sltech_move_id': self.id,
            })]
            if self.sltech_amount_tax:
                account_tax = self.env['account.account'].search(
                    [
                        # ('user_type_id', '=', self.env.ref('account.data_account_type_current_liabilities').id),
                        ('name', '=', 'Tax Paid'),
                        ('company_id', '=', self.company_id.id)], limit=1)
                line_ids += [(0, 0, {
                    'account_id': account_tax.id,
                    'name': account_tax.name,
                    'debit': self.sltech_amount_tax,
                    'sltech_move_id': self.id,
                })]

            self.sltech_move_id.write({
                'line_ids': [(5, 0)]
            })
            self.sltech_move_id.write({
                'line_ids': line_ids
            })

            self.sltech_move_id.action_post()

    def button_draft(self):
        res = super(AccountInvoice, self).button_draft()

        if self.sltech_move_id:
            self.sltech_move_id.button_draft()

        return res

    def action_post(self):
        res = super(AccountInvoice, self).action_post()

        self.sltech_action_post()

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
    price_untax = fields.Float('Untaxed Amount', store=True)
    tax_ids = fields.Many2many('account.tax', string='Taxes')

    payment_id = fields.Many2one('account.payment', 'Payment')
    payment_state = fields.Selection(related='payment_id.state')

    partial_payment_move_ids = fields.Many2many('account.move')

    amount_tax = fields.Float('Amount Tax')

    @api.onchange('product_id', 'tax_ids')
    def onchange_pro_id(self):
        if self.product_id:
            self.price_unit = self.product_id.list_price
            self.quantity = 1

            tax_details = self.tax_ids.compute_all(price_unit=self.price_unit, currency=False, quantity=self.quantity, product=self.product_id)

            self.price_subtotal = tax_details['total_included']
            self.price_untax = tax_details['total_excluded']
            self.amount_tax = abs(tax_details['total_included'] - tax_details['total_excluded'])

    @api.onchange('quantity', 'price_unit')
    def onchange_quantityprice_unit(self):
        tax_details = self.tax_ids.compute_all(price_unit=self.price_unit, currency=False, quantity=self.quantity,
                                               product=self.product_id)

        self.price_subtotal = tax_details['total_included']
        self.price_untax = tax_details['total_excluded']
        self.amount_tax = abs(tax_details['total_included'] - tax_details['total_excluded'])

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    sltech_move_id = fields.Many2one('account.move')