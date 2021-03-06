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
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        account_sale_tax_id = []
        account_purchase_tax_id = []
        for company_id in self.env['res.company'].sudo().search([]):
            account_sale_tax_id.append(
                company_id.account_sale_tax_id.id
            )
            account_purchase_tax_id.append(
                company_id.account_purchase_tax_id.id
            )
        self.sudo().write(dict(
            taxes_id=[(6, 0, account_sale_tax_id)],
            supplier_taxes_id=[(6, 0, account_purchase_tax_id)]
        ))
        return res
