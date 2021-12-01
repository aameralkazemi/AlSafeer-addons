# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging



_logger = logging.getLogger(__name__)


class ResCurrency(models.Model):
    _inherit = 'res.currency'



    def _get_rates(self, company, date):
        currency_rates = super(ResCurrency, self)._get_rates(company, date)
        key_foreign = 0
        if self.env.context.get('value_check_rate') and self.env.context.get('value_rate_exchange'):
            keys = list(currency_rates.keys())
            if currency_rates:
                for key in keys:
                    if key != company.currency_id.id:
                        key_foreign = key
            currency_rates[key_foreign] = 1.0 / self.env.context.get('value_rate_exchange')
        print(currency_rates)
        return currency_rates


