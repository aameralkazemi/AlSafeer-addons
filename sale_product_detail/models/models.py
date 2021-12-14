# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    sale_details_line_id = fields.One2many('sale.details.line','detail_id',string='Sale Detail')

class SaleDetailsLine(models.Model):
    _name = 'sale.details.line'

    detail_id = fields.Many2one('sale.order','Details')
    product_id = fields.Many2one('product.product','Product')
    quantity = fields.Float('Quantity')
    partner_id = fields.Many2one('res.partner','Customer')
    price_unit = fields.Float('Price Unit')
    invoice_id = fields.Many2one('account.move',string='Invoice')
    invoice_date = fields.Date('Invoice Date')

class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    def action_sale_details(self):
        if self.order_id.sale_details_line_id:
            for line in self.order_id.sale_details_line_id:
                line.unlink()
        detail_rec = self.env['account.move.line'].search([('move_id.partner_id','=',self.order_id.partner_id.id),('move_id.type','=','out_invoice'),('product_id','=',self.product_id.id)], order='id desc', limit=5)
        print(detail_rec,'========')
        if detail_rec:
            detail_line = []
            for x in detail_rec:
                if x.move_id.invoice_origin:
                    print(x.move_id.invoice_origin,'=======origin')
                    detail_line.append((0,0,{
                        'product_id':self.product_id.id,
                        'partner_id':self.order_id.partner_id.id,
                        'quantity':x.quantity,
                        'price_unit': x.price_unit,
                        'invoice_id': x.move_id.id,
                        'invoice_date':x.move_id.invoice_date
                    }))
            self.order_id.sale_details_line_id = detail_line
        if not detail_rec:
            detail_rec = self.env['account.move.line'].search(
                [('move_id.type', '=', 'out_invoice'),
                 ('product_id', '=', self.product_id.id)], order='id desc', limit=5)
            if detail_rec:
                detail_line = []
                for x in detail_rec:
                    if x.move_id.invoice_origin:
                        detail_line.append((0, 0, {
                            'product_id': self.product_id.id,
                            'partner_id': x.move_id.partner_id.id,
                            'quantity': x.quantity,
                            'price_unit': x.price_unit,
                            'invoice_id': x.move_id.id,
                            'invoice_date': x.move_id.invoice_date
                        }))
                self.order_id.sale_details_line_id = detail_line



