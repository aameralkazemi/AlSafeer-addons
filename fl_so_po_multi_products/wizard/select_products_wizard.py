# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api,_


class SelectProducts(models.TransientModel):

    _name = 'select.products'
    _description = 'Select Products'

    product_ids = fields.Many2many('product.product', string='Products')
    flag_order = fields.Char('Flag Order')

    def select_products(self):
        if self.flag_order == 'so':
            order_id = self.env['sale.order'].browse(self._context.get('active_id', False))
            for product in self.product_ids:
                tax_line_id=[]
                for tx_id in product.taxes_id:
                    tax_line_id.append(tx_id.id)
                self.env['sale.order.line'].create({
                    'product_id': product.id,
                    'product_uom': product.uom_id.id,
                    'price_unit': product.unit_price,
                    'product_uom_qty':product.so_qty,
                    'tax_id':[( 6, 0, tax_line_id)],
                    'order_id': order_id.id
                })
        elif self.flag_order == 'po':
            order_id = self.env['purchase.order'].browse(self._context.get('active_id', False))
            for product in self.product_ids:
                tax_line_id = []
                for tx_id in product.taxes_id:
                    tax_line_id.append(tx_id.id)
                self.env['purchase.order.line'].create({
                    'product_id': product.id,
                    'name': product.name,
                    'date_planned': order_id.date_planned or datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'product_uom': product.uom_id.id,
                    'product_qty': 1.0,
                    'price_unit': product.unit_price,
                    'product_uom_qty': product.so_qty,
                    'tax_id': [(6, 0, tax_line_id)],
                    'display_type': False,
                    'order_id': order_id.id

                })


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    so_qty=fields.Float('Quantity')
    unit_price=fields.Float('Unit Price')


class ProductProduct(models.Model):
    _inherit = 'product.product'


    def product_product_form_view_open(self):
        return {
            'name': _('Language Pack'),
            'view_mode': 'form',
            'view_id': self.env.ref('product.product_normal_form_view').id,
            'res_model': 'product.product',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }


