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
from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def write(self, vals):
        res = super(StockPicking, self).write(vals)

        return res


class StockMove(models.Model):
    _inherit = "stock.move"

    sltech_done_qty = fields.Float('Done')

    def write(self, vals):
        res = super(StockMove, self).write(vals)

        if vals.get('sltech_done_qty') and not self._context.get('sltech_stop_stoc_move'):

            move_line = self.env['stock.move.line']
            default_values = move_line.default_get(move_line._fields.keys())
            default_values.update({
                'qty_done': vals.get('sltech_done_qty'),
                # 'contact_display' : 'partner_address',
                # 'picking_type_code' : self.picking_id.picking_type_code,
                # 'active_id' : self.id,
                # 'active_ids' : self.ids,
                'picking_id' : self.picking_id.id,
                'location_id' : self.picking_id.location_id.id,
                'location_dest_id' : self.picking_id.location_dest_id.id,
                'company_id' : self.picking_id.company_id.id,
                'product_uom_id': self.product_uom.id,
                'product_id': self.product_id.id,
            })
            move_line = move_line.with_context(contact_display='partner_address',
                                               picking_type_code=self.picking_id.picking_type_code,
                                               active_id=self.id,
                                               active_ids=self.ids,
                                               default_picking_id=self.picking_id.id,
                                               default_location_id=self.picking_id.location_id.id,
                                               default_location_dest_id=self.picking_id.location_dest_id.id,
                                               default_company_id=self.picking_id.company_id.id,)
            move_line = move_line.create(default_values)

            self.move_line_nosuggest_ids = [(6, 0, [move_line.id])]

        return res

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.model
    def create(self, vals):
        res = super(StockMoveLine, self).create(vals)
        return res