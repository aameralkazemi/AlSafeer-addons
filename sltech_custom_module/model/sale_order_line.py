# -*- coding: utf-8 -*-
##############################################################################
#
#    SLTECH ERP SOLUTION
#    Copyright (C) 2022-Today(www.slecherpsolution.com).
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

from odoo import api, fields, models, _

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    _description = "Sales Order Line"

    partner_id = fields.Many2one('res.partner', string='Vendor Name', store=True)

    @api.onchange('product_id')
    def product_id_change_vendor(self):
        domain = super(SaleOrderLine, self).product_id_change()
        if self.product_id and self.product_id.seller_ids:
            self.partner_id = self.product_id.seller_ids[0].name
        return domain