# -*- coding: utf-8 -*-

from odoo import models, fields, api


class warning_price_below_cost_sale(models.Model):
    _inherit = 'sale.order.line'

    x_price_below_cost = fields.Boolean(compute='_price_unit', readonly=True, string='Price below Cost')

    @api.depends('price_unit')
    def _price_unit(self):
        for record in self:
            record['x_price_below_cost'] = (record.price_unit < record.product_id.standard_price)
