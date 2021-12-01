from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging



_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'


    check_rate = fields.Boolean(help='Amount of units of the base currency with respect to the foreign currency')
    rate_exchange= fields.Float(help='Amount of units of the base currency with respect to the foreign currency')
    local_currency_price = fields.Monetary()


    @api.onchange('amount', 'rate_exchange', 'check_rate')
    def currency_price(self):
        self.ensure_one()
        if self.check_rate:
            if self.rate_exchange:
                if not self.get_current_invoice_currency():
                    self.local_currency_price = None
                else:
                    self.local_currency_price = self.rate_exchange * self.amount
        else:
            self.local_currency_price = None

    @api.onchange('currency_id')
    def onchange_currency_id(self):
        self.ensure_one()
        if self.check_rate and self.rate_exchange:
            if not self.get_current_invoice_currency():
                self.local_currency_price = None
            else:
                self.local_currency_price = self.rate_exchange * self.amount
        else:
            if not self.get_current_invoice_currency():
                self.local_currency_price = None

    # - obtener la moneda que esta trabajando el invoice, saber si es diferente a la que tiene por defecto la empresa
    def get_current_invoice_currency(self):
        self.ensure_one()
        other_currency = False
        if self.company_id.currency_id.id != self.currency_id.id:
            other_currency = True
        return other_currency