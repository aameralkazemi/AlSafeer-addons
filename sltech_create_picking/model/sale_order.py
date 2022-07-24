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

class SaleOrder(models.Model):
    _inherit = "sale.order"
    _description = "Sales Order"

    def sltech_action_confirm(self):
        self.state = 'sale'

    def _create_invoices(self, grouped=False, final=False):
        res = super(SaleOrder, self)._create_invoices(grouped=grouped, final=final)
        for inv in self.invoice_ids:
            inv.sltech_sale_id = self.id
        return res