# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, api, _, fields
from odoo.exceptions import ValidationError

class AccountMove(models.AbstractModel):
    _inherit = "account.move"

    sltech_sale_id = fields.Many2one('sale.order')

    def action_post(self):
        res = super(AccountMove, self).action_post()
        picking_id = False
        for rec in self:
            if rec.type == 'out_invoice':
                sale_id = rec.sltech_sale_id
                if not sale_id:
                    sale_id = self.env['sale.order'].search([('invoice_ids', 'in', rec.ids)])
                sale_id.state = 'draft'
                sale_id.action_confirm()
                picking_id = sale_id.picking_ids.filtered(lambda obj: obj.state in ['waiting', 'confirmed', 'assigned'])

            elif rec.type == 'out_refund':
                sale_id = rec.sltech_sale_id
                if not sale_id:
                    sale_id = self.env['sale.order'].search([('invoice_ids', 'in', rec.ids)])
                picking_id = sale_id.picking_ids.filtered(lambda obj: obj.state in ['done'])
                StockReturnPicking = self.env['stock.return.picking'].with_context(
                    active_id=picking_id.id,
                    active_ids=picking_id.ids,
                    active_model='stock.picking',
                )
                default_values = StockReturnPicking.default_get(StockReturnPicking._fields.keys())
                return_picking_id = StockReturnPicking.create(default_values)
                return_picking_id._onchange_picking_id()
                new_picking_id, pick_type_id = return_picking_id._create_returns()
                picking_id = self.env['stock.picking'].browse(new_picking_id)

            if picking_id:
                picking_id.action_assign()
                rec = picking_id.button_validate()
                if rec.get('res_model'):
                    record_id = self.env[rec['res_model']].browse(rec['res_id'])
                    if rec['res_model'] == 'confirm.stock.sms':
                        record_id.send_sms()
                    elif rec['res_model'] == 'stock.immediate.transfer':
                        record_id.process()
                    if rec['res_model'] == 'stock.overprocessed.transfer':
                        record_id.action_confirm()

                if picking_id.state != 'done':
                    raise ValidationError("You don't have enough stock to validate!")

        return res