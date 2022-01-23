# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import UserError, ValidationError

class account_account(models.Model):
    _inherit = 'account.account'
    
    discount_account = fields.Boolean('Discount Account')
    


class account_move(models.Model):
    _inherit = 'account.move'

    is_line = fields.Boolean('Is a line')
   
    def calc_discount(self):
        for calculate in self:
            calculate._calculate_discount()

    @api.depends('discount_amount','discount_method',)
    def _calculate_discount(self):
        res = discount = 0.0
        for self_obj in self:
            if self_obj.discount_type == 'global':
                if self_obj.discount_method == 'fix':
                    res = self_obj.discount_amount
                elif self_obj.discount_method == 'per':
                    res_config = self.env.user.company_id
                    if res_config and res_config.tax_discount_policy == 'tax':
                        res = (self_obj.amount_untaxed + self_obj.amount_tax) * (self_obj.discount_amount/ 100)
                    else:
                        res = self_obj.amount_untaxed * (self_obj.discount_amount/ 100)
            else:
                res = discount
        return res



    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state','discount_method','discount_amount')
    def _compute_amount(self):
        invoice_ids = [move.id for move in self if move.id and move.is_invoice(include_receipts=True)]
        self.env['account.payment'].flush(['state'])
        if invoice_ids:
            self._cr.execute(
                '''
                    SELECT move.id
                    FROM account_move move
                    JOIN account_move_line line ON line.move_id = move.id
                    JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
                    JOIN account_move_line rec_line ON
                        (rec_line.id = part.debit_move_id AND line.id = part.credit_move_id)
                    JOIN account_payment payment ON payment.id = rec_line.payment_id
                    JOIN account_journal journal ON journal.id = rec_line.journal_id
                    WHERE payment.state IN ('posted', 'sent')
                    AND journal.post_at = 'bank_rec'
                    AND move.id IN %s
                UNION
                    SELECT move.id
                    FROM account_move move
                    JOIN account_move_line line ON line.move_id = move.id
                    JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
                    JOIN account_move_line rec_line ON
                        (rec_line.id = part.credit_move_id AND line.id = part.debit_move_id)
                    JOIN account_payment payment ON payment.id = rec_line.payment_id
                    JOIN account_journal journal ON journal.id = rec_line.journal_id
                    WHERE payment.state IN ('posted', 'sent')
                    AND journal.post_at = 'bank_rec'
                    AND move.id IN %s
                ''', [tuple(invoice_ids), tuple(invoice_ids)]
            )
            in_payment_set = set(res[0] for res in self._cr.fetchall())
        else:
            in_payment_set = {}

        for move in self:
            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            currencies = set()

            for line in move.line_ids:
                if line.currency_id:
                    currencies.add(line.currency_id)

                if move.is_invoice(include_receipts=True):
                    # === Invoices ===

                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                        # Residual amount.
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if move.type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1
            move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
            move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
            move.amount_total = sign * (total_currency if len(currencies) == 1 else total)
            move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(total) if move.type == 'entry' else -total
            move.amount_residual_signed = total_residual
            res = move._calculate_discount()
            move.discount_amt = res
            move.amount_total = (move.amount_untaxed + move.amount_tax) - res

            currency = len(currencies) == 1 and currencies.pop() or move.company_id.currency_id
            is_paid = currency and currency.is_zero(move.amount_residual) or not move.amount_residual

            # Compute 'invoice_payment_state'.
            if move.type == 'entry':
                move.invoice_payment_state = False
            elif move.state == 'posted' and is_paid:
                if move.id in in_payment_set:
                    move.invoice_payment_state = 'in_payment'
                else:
                    move.invoice_payment_state = 'paid'
            else:
                move.invoice_payment_state = 'not_paid'

        res_config = self.env.user.company_id
        if res_config:
            for rec in self:
                if res_config.tax_discount_policy == 'tax':
                    if rec.discount_type == 'line':
                        rec.discount_amt = 0.00
                        total = 0
                        if self._context.get('default_type') in ('in_invoice','out_invoice','out_refund','in_refund'):
                            for line in self.invoice_line_ids:
                                if line.discount_method == 'per':
                                    total += line.price_total * (line.discount_amount/ 100)
                                elif line.discount_method == 'fix':
                                    total += line.discount_amount
                            rec.discount_amt_line = total
                        if self._context.get('default_type') in ('out_invoice','out_refund'):
                            if rec.discount_amount_line > 0.0:
                                rec.discount_amt_line = rec.discount_amount_line
                        rec.amount_total = rec.amount_tax + rec.amount_untaxed - rec.discount_amt_line
                        rec.amount_total_signed = abs(rec.amount_total) if move.type == 'entry' else -rec.amount_total
                    elif rec.discount_type == 'global':
                        if rec.discount_method == 'fix':
                            rec.amount_total = rec.amount_tax + rec.amount_untaxed - rec.discount_amt
                            rec.amount_total_signed = abs(rec.amount_total) if move.type == 'entry' else -rec.amount_total
                        elif rec.discount_method == 'per':
                            rec.amount_total = rec.amount_tax + rec.amount_untaxed - rec.discount_amt
                            rec.amount_total_signed = abs(rec.amount_total) if move.type == 'entry' else -rec.amount_total
                        
                        else:
                            rec.amount_total = rec.amount_tax + rec.amount_untaxed
                            rec.amount_total_signed = abs(rec.amount_total) if move.type == 'entry' else -rec.amount_total

                    else:
                        rec.amount_total = rec.amount_tax + rec.amount_untaxed
                elif res_config.tax_discount_policy == 'untax':
                    sums = 0.00
                    if rec.discount_type == 'line':
                        total = 0
                        if self._context.get('default_type') in ('in_invoice','out_invoice','out_refund','in_refund'):

                            for line in self.invoice_line_ids:
                                if line.discount_method == 'per':
                                    total += line.price_subtotal * (line.discount_amount/ 100)
                                elif line.discount_method == 'fix':
                                    total += line.discount_amount
                            rec.discount_amt_line = total

                        if self._context.get('default_type') in ('out_invoice','out_refund') :
                            if rec.discount_amount_line > 0.0:
                                rec.discount_amt_line = rec.discount_amount_line

                        rec.amount_total = rec.amount_tax + rec.amount_untaxed - rec.discount_amt_line        
                        rec.amount_total_signed = abs(rec.amount_total) if move.type == 'entry' else -rec.amount_total
                        rec.discount_amt = 0.00

                    elif rec.discount_type == 'global':
                        if rec.discount_method == 'fix':
                            if rec.invoice_line_ids:
                                for line in rec.invoice_line_ids:
                                    if line.tax_ids:
                                        if rec.amount_untaxed:
                                            final_discount = ((rec.discount_amt*line.price_subtotal)/rec.amount_untaxed)
                                            discount = line.price_subtotal - final_discount
                                            taxes = line.tax_ids.compute_all(discount, rec.currency_id, 1.0,
                                                                            line.product_id,rec.partner_id)
                                            sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                            rec.amount_total = rec.amount_tax + rec.amount_untaxed - rec.discount_amt
                            rec.amount_total_signed = abs(rec.amount_total) if move.type == 'entry' else -rec.amount_total

                        elif rec.discount_method == 'per':
                            if rec.invoice_line_ids:
                                for line in rec.invoice_line_ids:
                                    if line.tax_ids:
                                        final_discount = ((rec.discount_amount*line.price_subtotal)/100.0)
                                        discount = line.price_subtotal - final_discount
                                        taxes = line.tax_ids.compute_all(discount, rec.currency_id, 1.0,
                                                                        line.product_id,rec.partner_id)
                                        sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                        
                            rec.amount_total = rec.amount_tax + rec.amount_untaxed - rec.discount_amt
                            rec.amount_total_signed = abs(rec.amount_total) if move.type == 'entry' else -rec.amount_total

                    else:
                        rec.amount_total = rec.amount_tax + rec.amount_untaxed - rec.discount_amt
                        rec.amount_total_signed = abs(rec.amount_total) if move.type == 'entry' else -rec.amount_total

                else:
                    rec.amount_total = rec.amount_tax + rec.amount_untaxed - rec.discount_amt    
                    rec.amount_total_signed = abs(rec.amount_total) if move.type == 'entry' else -rec.amount_total


                if rec.discount_type and (rec.discount_method in ["fix","per"] and rec.discount_amount != 0 \
                    or any(l.discount_method in ["fix","per"] and l.discount_amount > 0 for l in rec.invoice_line_ids)):
                    if rec.type in ('out_invoice','out_refund'):
                        if res_config.sale_account_id:
                            rec.discount_account_id = res_config.sale_account_id.id
                            
                        else:
                            account_id = False
                            account_id = rec.env['account.account'].search([('user_type_id.name','=','Expenses'), ('discount_account','=',True)],limit=1)
                            if not account_id:
                                raise UserError(_('Please define an sale discount account for this company.'))
                            else:
                                rec.discount_account_id = account_id.id

                    if rec.type in ('in_invoice','in_refund'):
                        if res_config.purchase_account_id:
                            rec.discount_account_id = res_config.purchase_account_id.id
                        else:
                            account_id = False
                            account_id = rec.env['account.account'].search([('user_type_id.name','=','Income'), ('discount_account','=',True)],limit=1)
                            if not account_id:
                                raise UserError(_('Please define an purchase discount account for this company.'))
                            else:
                                rec.discount_account_id = account_id.id        

            
    discount_method = fields.Selection([('fix', 'Fixed'), ('per', 'Percentage')],'Discount Method')
    discount_amount = fields.Float('Discount Amount')
    discount_amt = fields.Float(string='- Discount', readonly=True, compute='_compute_amount')
    amount_untaxed = fields.Monetary(string='Subtotal', digits="Account",store=True, readonly=True, compute='_compute_amount',track_visibility='always')
    amount_tax = fields.Float(string='Tax', digits="Account",store=True, readonly=True, compute='_compute_amount')
    amount_total = fields.Monetary(string='Total', digits="Account",store=True, readonly=True, compute='_compute_amount')
    discount_type = fields.Selection([('line', 'Order Line'), ('global', 'Global')], 'Discount Applies to',default='global')
    discount_account_id = fields.Many2one('account.account', 'Discount Account',compute='_compute_amount',store=True)
    discount_amt_line = fields.Float(compute='_compute_amount', string='- Line Discount', digits="Account", store=True, readonly=True)
    discount_amount_line = fields.Float(string="Discount Line")
   

    def _recompute_tax_lines(self, recompute_tax_base_amount=False):
        """ Compute the dynamic tax lines of the journal entry.

        :param recompute_tax_base_amount: Flag forcing only the recomputation of the `tax_base_amount` field.
        """
        self.ensure_one()
        in_draft_mode = self != self._origin

        def _serialize_tax_grouping_key(grouping_dict):
            ''' Serialize the dictionary values to be used in the taxes_map.
            :param grouping_dict: The values returned by '_get_tax_grouping_key_from_tax_line' or '_get_tax_grouping_key_from_base_line'.
            :return: A string representing the values.
            '''
            return '-'.join(str(v) for v in grouping_dict.values())

        def _compute_base_line_taxes(base_line):
            ''' Compute taxes amounts both in company currency / foreign currency as the ratio between
            amount_currency & balance could not be the same as the expected currency rate.
            The 'amount_currency' value will be set on compute_all(...)['taxes'] in multi-currency.
            :param base_line:   The account.move.line owning the taxes.
            :return:            The result of the compute_all method.
            '''
            move = base_line.move_id
            if move.is_invoice(include_receipts=True):
                handle_price_include = True
                sign = -1 if move.is_inbound() else 1
                quantity = base_line.quantity
                price_unit_wo_discount = sign * base_line.price_unit * (1 - (base_line.discount / 100.0))
                tax_type = 'sale' if move.type.startswith('out_') else 'purchase'
                is_refund = move.type in ('out_refund', 'in_refund')
            else:
                handle_price_include = False
                quantity = 1.0
                price_unit_wo_discount = base_line.amount_currency if base_line.currency_id else base_line.balance
                tax_type = base_line.tax_ids[0].type_tax_use if base_line.tax_ids else None
                is_refund = (tax_type == 'sale' and base_line.debit) or (tax_type == 'purchase' and base_line.credit)

            if move.discount_type and (move.discount_method in ["fix","per"] and move.discount_amount != 0 \
                    or any(l.discount_method in ["fix","per"] and l.discount_amount != 0 for l in move.invoice_line_ids)):
                res_config = self.env.user.company_id
                if res_config:
                    for rec in self:
                        if res_config.tax_discount_policy == 'untax':
                            if rec.discount_type == 'line':
                                if base_line.discount_method == 'fix':
                                    if base_line.discount_amount > 0:
                                        price_unit_wo_discount = base_line.price_unit - rec.currency_id.round(base_line.discount_amount / base_line.quantity)
                                        if move.is_invoice(include_receipts=True):
                                            sign = -1 if move.is_inbound() else 1
                                            price_unit_wo_discount = sign * price_unit_wo_discount
                                
                                elif base_line.discount_method == 'per':
                                    if base_line.discount_amount > 0:
                                        price_unit_wo_discount = base_line.price_unit * (1 - (base_line.discount_amount / 100.0))
                                        if move.is_invoice(include_receipts=True):
                                            sign = -1 if move.is_inbound() else 1
                                            price_unit_wo_discount = sign * price_unit_wo_discount

                            elif rec.discount_type == 'global':
                                if rec.discount_amount > 0:
                                    if rec.amount_untaxed != 0.0:
                                        final_discount = ((rec.discount_amt*base_line.price_unit)/rec.amount_untaxed)
                                        price_unit_wo_discount = base_line.price_unit - rec.currency_id.round(final_discount)
                                        if move.is_invoice(include_receipts=True):
                                            quantity = base_line.quantity
                                            sign = -1 if move.is_inbound() else 1
                                            price_unit_wo_discount = sign * price_unit_wo_discount
                                    else:
                                        final_discount = (rec.discount_amt*base_line.price_unit)/1.0
                                        discount = base_line.price_unit - rec.currency_id.round(final_discount)


            balance_taxes_res = base_line.tax_ids._origin.with_context(force_sign=move._get_tax_force_sign()).compute_all(
                price_unit_wo_discount,
                currency=base_line.currency_id or base_line.company_currency_id,
                quantity=quantity,
                product=base_line.product_id,
                partner=base_line.partner_id,
                is_refund=is_refund,
                handle_price_include=handle_price_include,
            )

            if move.type == 'entry':
                repartition_field = is_refund and 'refund_repartition_line_ids' or 'invoice_repartition_line_ids'
                repartition_tags = base_line.tax_ids.flatten_taxes_hierarchy().mapped(repartition_field).filtered(lambda x: x.repartition_type == 'base').tag_ids
                tags_need_inversion = self._tax_tags_need_inversion(move, is_refund, tax_type)
                if tags_need_inversion:
                    balance_taxes_res['base_tags'] = base_line._revert_signed_tags(repartition_tags).ids
                    for tax_res in balance_taxes_res['taxes']:
                        tax_res['tag_ids'] = base_line._revert_signed_tags(self.env['account.account.tag'].browse(tax_res['tag_ids'])).ids

            return balance_taxes_res

        taxes_map = {}

        # ==== Add tax lines ====
        to_remove = self.env['account.move.line']
        for line in self.line_ids.filtered('tax_repartition_line_id'):
            grouping_dict = self._get_tax_grouping_key_from_tax_line(line)
            grouping_key = _serialize_tax_grouping_key(grouping_dict)
            if grouping_key in taxes_map:
                # A line with the same key does already exist, we only need one
                # to modify it; we have to drop this one.
                to_remove += line
            else:
                taxes_map[grouping_key] = {
                    'tax_line': line,
                    'amount': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                }
        if not recompute_tax_base_amount:
            self.line_ids -= to_remove

        # ==== Mount base lines ====
        for line in self.line_ids.filtered(lambda line: not line.tax_repartition_line_id):
            # Don't call compute_all if there is no tax.
            if not line.tax_ids:
                if not recompute_tax_base_amount:
                    line.tag_ids = [(5, 0, 0)]
                continue

            compute_all_vals = _compute_base_line_taxes(line)

            # Assign tags on base line
            if not recompute_tax_base_amount:
                line.tag_ids = compute_all_vals['base_tags'] or [(5, 0, 0)]

            tax_exigible = True
            for tax_vals in compute_all_vals['taxes']:
                grouping_dict = self._get_tax_grouping_key_from_base_line(line, tax_vals)
                grouping_key = _serialize_tax_grouping_key(grouping_dict)

                tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_vals['tax_repartition_line_id'])
                tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id

                if tax.tax_exigibility == 'on_payment':
                    tax_exigible = False

                taxes_map_entry = taxes_map.setdefault(grouping_key, {
                    'tax_line': None,
                    'amount': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                })
                taxes_map_entry['amount'] += tax_vals['amount']
                taxes_map_entry['tax_base_amount'] += self._get_base_amount_to_display(tax_vals['base'], tax_repartition_line, tax_vals['group'])
                taxes_map_entry['grouping_dict'] = grouping_dict
            if not recompute_tax_base_amount:
                line.tax_exigible = tax_exigible

        # ==== Pre-process taxes_map ====
        taxes_map = self._preprocess_taxes_map(taxes_map)

        # ==== Process taxes_map ====
        for taxes_map_entry in taxes_map.values():
            tax_line = taxes_map_entry['tax_line']

            # The tax line is no longer used in any base lines, drop it.
            if tax_line and not taxes_map_entry['grouping_dict']:
                if not recompute_tax_base_amount:
                    self.line_ids -= tax_line
                continue

            currency_id = taxes_map_entry['grouping_dict']['currency_id']
            currency = self.env['res.currency'].browse(currency_id) if currency_id else False
            conversion_date = self.date or fields.Date.context_today(self)

            # Don't create tax lines with zero balance.
            if (currency or self.company_currency_id).is_zero(taxes_map_entry['amount']):
                if taxes_map_entry['tax_line'] and not recompute_tax_base_amount:
                    self.line_ids -= taxes_map_entry['tax_line']
                continue

            # tax_base_amount field is expressed using the company currency.
            if currency:
                tax_base_amount = currency._convert(taxes_map_entry['tax_base_amount'], self.company_currency_id, self.company_id, conversion_date)
            else:
                tax_base_amount = taxes_map_entry['tax_base_amount']

            # Recompute only the tax_base_amount.
            if recompute_tax_base_amount:
                if taxes_map_entry['tax_line']:
                    taxes_map_entry['tax_line'].tax_base_amount = tax_base_amount
                continue

            if currency:
                amount_currency = taxes_map_entry['amount']
                balance = currency._convert(amount_currency, self.company_currency_id, self.company_id, conversion_date)
            else:
                amount_currency = 0.0
                balance = taxes_map_entry['amount']

            to_write_on_line = {
                'amount_currency': amount_currency,
                'debit': balance > 0.0 and balance or 0.0,
                'credit': balance < 0.0 and -balance or 0.0,
                'tax_base_amount': tax_base_amount,
            }

            if taxes_map_entry['tax_line']:
                # Update an existing tax line.
                taxes_map_entry['tax_line'].update(to_write_on_line)
            else:
                # Create a new tax line.
                create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create
                tax_repartition_line_id = taxes_map_entry['grouping_dict']['tax_repartition_line_id']
                tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_repartition_line_id)
                tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id
                taxes_map_entry['tax_line'] = create_method({
                    **to_write_on_line,
                    'name': tax.name,
                    'move_id': self.id,
                    'partner_id': line.partner_id.id,
                    'company_id': line.company_id.id,
                    'company_currency_id': line.company_currency_id.id,
                    'quantity': 1.0,
                    'date_maturity': False,
                    'exclude_from_invoice_tab': True,
                    'tax_exigible': tax.tax_exigibility == 'on_invoice',
                    **taxes_map_entry['grouping_dict'],
                })

            if in_draft_mode:
                taxes_map_entry['tax_line']._onchange_amount_currency()
                taxes_map_entry['tax_line']._onchange_balance()



    @api.model_create_multi
    def create(self, vals_list):
        result = super(account_move,self).create(vals_list)
        for res in result:
            if res.type != "entry":
                if res.discount_type and res.discount_method in ["fix","per"] and (res.discount_method in ["fix","per"] and res.discount_amount != 0 \
                    or any(l.discount_method in ["fix","per"] and l.discount_amount != 0 for l in res.invoice_line_ids)):
                    
                    line = res.line_ids.filtered(lambda s: s.name == "Discount");
                    
                    if res.discount_type == 'line':
                        price = res.discount_amt_line
                    elif res.discount_type == 'global':
                        price = res.discount_amt
                    else:
                        price = 0  
                    
                    if len(line or []) == 0:
                        if res.discount_account_id:       
                            discount_vals = {
                                    'account_id': res.discount_account_id, 
                                    'quantity': 1,
                                    'price_unit': -price,
                                    'name': "Discount", 
                                    'exclude_from_invoice_tab': True,
                                }    
                            res.with_context(check_move_validity=False).write({
                                    'invoice_line_ids' : [(0,0,discount_vals)]
                                })
                        else:
                            pass    
        return result



    @api.onchange('invoice_line_ids','discount_amount','discount_method')
    def _onchange_invoice_line_ids_discount(self):
        for res in self:
            res._compute_amount()
            if res.type != "entry":
                if res.discount_type and (res.discount_method in ["fix","per"] and res.discount_amount != 0 \
                    or any(l.discount_method in ["fix","per"] and l.discount_amount != 0 for l in res.invoice_line_ids)):
                    
                    line = res.line_ids.filtered(lambda s: s.name == "Discount");
                    
                    if res.discount_type == 'line':
                        price = res.discount_amt_line
                    elif res.discount_type == 'global':
                        price = res.discount_amt
                    else:
                        price = 0  
                    
                    if len(line or []) == 0:
                        if res.discount_account_id:       
                            discount_vals = {
                                    'account_id': res.discount_account_id, 
                                    'quantity': 1,
                                    'price_unit': -price,
                                    'name': "Discount", 
                                    'exclude_from_invoice_tab': True,
                                }    
                            res.with_context(check_move_validity=False).update({
                                    'invoice_line_ids' : [(0,0,discount_vals)]
                                    })
                        else:
                            pass
            

        if res.discount_type and (res.discount_method in ["fix","per"] and res.discount_amount != 0 \
                    or any(l.discount_method in ["fix","per"] and l.discount_amount > 0 for l in res.invoice_line_ids)):
            
            if self.discount_type == 'line':
                price = self.discount_amt_line
            elif self.discount_type == 'global':
                price = self.discount_amt
            else:
                price = 0
            for rec in self.line_ids:
                if self._context.get('default_type') in ('out_invoice','in_refund'):
                    if rec.name == "Discount":
                        rec.with_context(check_move_validity=False).write({'debit':price})
                    if rec.name == False or rec.name == '':
                        rec.with_context(check_move_validity=False).write({'debit':self.amount_total})
                
                elif self._context.get('default_type') in ('in_invoice','out_refund'):
                    if rec.name == "Discount":
                        rec.with_context(check_move_validity=False).write({'credit':price})
                    if rec.name == False or rec.name == '':
                        rec.with_context(check_move_validity=False).write({'credit':self.amount_total})
                else:
                    pass


    def write(self,vals):
        result = super(account_move, self).write(vals)
        for res in self:
            if res.type != "entry":
                if res.discount_type and (res.discount_method in ["fix","per"] and res.discount_amount != 0 \
                    or any(l.discount_method in ["fix","per"] and l.discount_amount != 0 for l in res.invoice_line_ids)):
                    
                    line = res.line_ids.filtered(lambda s: s.name == "Discount");
                    
                    if res.discount_type == 'line':
                        price = res.discount_amt_line
                    elif res.discount_type == 'global':
                        price = res.discount_amt
                    else:
                        price = 0  
                    
                    if len(line or []) == 0:
                        if res.discount_account_id:       
                            discount_vals = {
                                    'account_id': res.discount_account_id, 
                                    'quantity': 1,
                                    'price_unit': -price,
                                    'name': "Discount", 
                                    'exclude_from_invoice_tab': True,
                                }  
                            vals["invoice_line_ids"].append([(0,0,discount_vals)])  
                            res.with_context(check_move_validity=False).update({
                                    'invoice_line_ids' : [(0,0,discount_vals)]
                                    })
                        else:
                            pass
        return result  


    @api.onchange('discount_amount','discount_method')
    def _onchange_taxes(self):
        ''' Recompute the dynamic onchange based on taxes.
        If the edited line is a tax line, don't recompute anything as the user must be able to
        set a custom value.
        '''
        for line in self.line_ids:
            if not line.tax_repartition_line_id:
                line.recompute_tax_line = True
        self._recompute_dynamic_lines()
    

    

class account_move_line(models.Model):
    _inherit = 'account.move.line'
 
    discount_method = fields.Selection([('fix', 'Fixed'), ('per', 'Percentage')], 'Discount Method')
    discount_type = fields.Selection(related='move_id.discount_type', string="Discount Applies to")
    discount_amount = fields.Float('Discount Amount')
    discount_amt = fields.Float('Discount Final Amount')

    @api.onchange('discount_method','discount_amount','amount_currency', 'currency_id', 'debit', 'credit', 'tax_ids', 'account_id',)
    def _onchange_mark_recompute_taxes(self):
        ''' Recompute the dynamic onchange based on taxes.
        If the edited line is a tax line, don't recompute anything as the user must be able to
        set a custom value.
        '''
        for line in self:
            if not line.tax_repartition_line_id:
                line.recompute_tax_line = True
                
                
                

class ResCompany(models.Model):
    _inherit = 'res.company'

    tax_discount_policy = fields.Selection([('tax', 'Tax Amount'), ('untax', 'Untax Amount')],
        default_model='sale.order',default='tax')
    sale_account_id = fields.Many2one('account.account',domain=[('user_type_id.name','=','Expenses'), ('discount_account','=',True)])
    purchase_account_id = fields.Many2one('account.account',domain=[('user_type_id.name','=','Income'), ('discount_account','=',True)])


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tax_discount_policy = fields.Selection([('tax', 'Tax Amount'), ('untax', 'Untax Amount')],readonly=False,related='company_id.tax_discount_policy',string='Discount Applies On',default_model='sale.order'
        )
    sale_account_id = fields.Many2one('account.account',string='Sale Discount Account',domain=[('user_type_id.name','=','Expenses'), ('discount_account','=',True)],readonly=False,related='company_id.sale_account_id')
    purchase_account_id = fields.Many2one('account.account',string='Purchase Discount Account',domain=[('user_type_id.name','=','Income'), ('discount_account','=',True)],readonly=False,related='company_id.purchase_account_id')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        tax_discount_policy = ICPSudo.get_param('bi_invoice_discount_with_tax.tax_discount_policy')
        sale_account_id = ICPSudo.get_param('bi_invoice_discount_with_tax.sale_account_id')
        purchase_account_id = ICPSudo.get_param('bi_invoice_discount_with_tax.purchase_account_id')
        res.update(tax_discount_policy=tax_discount_policy,sale_account_id=int(sale_account_id),purchase_account_id=int(purchase_account_id),)
        return res

    def set_values(self):

        super(ResConfigSettings, self).set_values()
        for rec in self:
            ICPSudo = rec.env['ir.config_parameter'].sudo()
            ICPSudo.set_param('bi_invoice_discount_with_tax.sale_account_id',rec.sale_account_id.id)
            ICPSudo.set_param('bi_invoice_discount_with_tax.purchase_account_id',rec.purchase_account_id.id)
            ICPSudo.set_param('bi_invoice_discount_with_tax.tax_discount_policy',rec.tax_discount_policy)