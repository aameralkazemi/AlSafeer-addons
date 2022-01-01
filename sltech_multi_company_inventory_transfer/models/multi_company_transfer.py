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
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class KsStockTransferMultiCompany(models.Model):
    _inherit = "multicompany.transfer.stock"

    def ks_confirm_inventory_transfer(self):
        move_lines = [(0, 0, {
            'name': i.ks_product_id.name,
            'product_id': i.ks_product_id.id,
            'quantity_done': i.ks_qty_transfer,
            'product_uom_qty': i.ks_qty_transfer,
            'product_uom': i.ks_product_uom_type.id
        }) for i in self.ks_multicompany_transfer_stock_ids]
        self.name = self.env['ir.sequence'].with_context(ir_sequence_date=self.ks_schedule_date). \
            next_by_code("multicompany.transfer.inventory")
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'outgoing'),
            ('warehouse_id.company_id', '=', self.ks_transfer_from.id),
        ], limit=1)
        if not picking_type:
            raise ValidationError("Outgoing Picking is not defined for %s" % (self.ks_transfer_from.name))
        ks_picking_from_id = self.env['stock.picking'].create({
            'picking_type_id': picking_type.id,
            'location_id': self.ks_transfer_from_location.id,
            'partner_id': self.ks_transfer_to.partner_id.id,
            'scheduled_date': self.ks_schedule_date,
            'move_lines': move_lines,
            'origin': self.name,
            'location_dest_id': self.env['stock.location'].search([('usage', '=', 'customer'), '|',
                                                                   ('company_id', '=', self.ks_transfer_from.id),
                                                                   ('company_id', '=', False),

                                                                   ], limit=1, order='company_id desc').id,
        })
        ks_picking_from_id.with_context(from_company_id=self.ks_transfer_from.id,
                                        from_partner_id=self.ks_transfer_from.partner_id.id,
                                        to_partner_id=self.ks_transfer_to.partner_id.id,
                                      to_company_id=self.ks_transfer_to.id,
                                      sltech_change_account=True).button_validate()
        picking_incoming_id = self.env['stock.picking.type'].search([
            ('code', '=', 'incoming'),
            ('warehouse_id.company_id', '=', self.ks_transfer_to.id),
        ], limit=1)
        if not picking_incoming_id:
            raise ValidationError("Incoming Picking is not defined for %s" % (self.ks_transfer_to.name))
        ks_picking_to_id = self.env['stock.picking'].create({
            'picking_type_id': picking_incoming_id.id,
            'location_id': self.env['stock.location'].search([('usage', '=', 'supplier'), '|',
                                                              ('company_id', '=', self.ks_transfer_to.id),
                                                              ('company_id', '=', False)
                                                              ], limit=1, order='company_id desc').id,
            'partner_id': self.ks_transfer_from.partner_id.id,
            'scheduled_date': self.ks_schedule_date,
            'move_lines': move_lines,
            'origin': self.name,
            'location_dest_id': self.ks_transfer_to_location.id
        })
        ks_picking_to_id.with_context(from_company_id=self.ks_transfer_from.id,
                                        from_partner_id=self.ks_transfer_from.partner_id.id,
                                        to_partner_id=self.ks_transfer_to.partner_id.id,
                                      to_company_id=self.ks_transfer_to.id,
                                      sltech_change_account=True).button_validate()
        self.state = 'posted'
        self.ks_stock_picking_ids = [(6, 0, [ks_picking_from_id.id, ks_picking_to_id.id])]
