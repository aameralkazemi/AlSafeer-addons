# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountInvoiceCustomCoditeq(models.Model):
    _inherit = 'account.move'

    check_rate = fields.Boolean(help='Amount of units of the base currency with respect to the foreign currency')
    rate_exchange = fields.Float(help='Amount of units of the base currency with respect to the foreign currency')

    def reset_trm_manual_is_calc_in_invoice_line_ids(self):
        self.ensure_one()
        for item in self.invoice_line_ids:
            item.trm_manual_is_calc = False
        for item in self.line_ids:
            item.trm_manual_is_calc = False

    @api.onchange('check_rate', 'rate_exchange', 'invoice_line_ids')
    def line_ids_invoice(self):
        self.ensure_one()
        if self.invoice_line_ids:
            if self.check_rate == False:
                for data in self.invoice_line_ids:
                    data.local_currency_price = None
                if self.get_current_invoice_currency():
                    self.reset_trm_manual_is_calc_in_invoice_line_ids()
                    self._manual_trm_mgmnt(False)
            else:
                if self.rate_exchange:
                    for data in self.invoice_line_ids:
                        data.local_currency_price = data.quantity * data.price_unit * self.rate_exchange

                    if self.get_current_invoice_currency():
                        self.reset_trm_manual_is_calc_in_invoice_line_ids()
                        self._manual_trm_mgmnt(True)

    @api.onchange('currency_id')
    def onchange_currency_id(self):
        self.ensure_one()
        if self.invoice_line_ids:
            if self.check_rate and self.rate_exchange:
                for data in self.invoice_line_ids:
                    data.local_currency_price = data.quantity * data.price_unit * self.rate_exchange
                if self.get_current_invoice_currency():
                    self.reset_trm_manual_is_calc_in_invoice_line_ids()
                    self._manual_trm_mgmnt(True)

    # - obtener la moneda que esta trabajando el invoice, saber si es diferente a la que tiene por defecto la empresa
    def get_current_invoice_currency(self):
        self.ensure_one()
        other_currency = False
        if self.company_id.currency_id.id != self.currency_id.id:
            other_currency = True
        return other_currency

    def get_current_trm(self):
        self.ensure_one()
        return round(1 / self.currency_id.rate, 2) if self.currency_id.rate else 0.00

    # - si se define la TRM manual, se modifican los apuntes contables
    # - @is_manual_trm = si True se esta manejando TRM manual
    def _manual_trm_mgmnt(self, is_manual_trm):
        self.ensure_one()
        ctx = self.env.context.copy()
        vlr_operar = self.rate_exchange if is_manual_trm else self.get_current_trm()
        for item in self.line_ids:

            if not item.trm_manual_is_calc:
                ctx.update({
                    'check_move_validity': False,  # - permite crear asientos contables desbalanceados
                })
                item.with_context(ctx).write({
                    'debit': 0.00 if item.debit == 0.00 else abs(item.amount_currency) * vlr_operar,
                    'credit': 0.00 if item.credit == 0.00 else abs(item.amount_currency) * vlr_operar
                })
            item.trm_manual_is_calc = True

    @api.model
    def create(self, vals):
        self.env.context = dict(self.env.context)
        self.env.context.update({
            'value_check_rate': True if 'check_rate' in vals and vals['check_rate'] else False,
            'value_rate_exchange': vals['rate_exchange'] if 'rate_exchange' in vals and vals['rate_exchange'] else None,
        })
        res = super(AccountInvoiceCustomCoditeq, self).create(vals)
        return res

class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    local_currency_price = fields.Float()
    trm_manual_is_calc = fields.Boolean(default=False)

    @api.onchange('move_id.rate_exchange', 'price_unit', 'quantity')
    def account_invoice_line_change_cry(self):
        self.ensure_one()
        if self.move_id.check_rate and self.move_id.rate_exchange:
            self.local_currency_price = self.quantity * self.price_unit * self.move_id.rate_exchange