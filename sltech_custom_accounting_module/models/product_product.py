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

class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def create(self, vals):
        account_sale_tax_id = []
        account_purchase_tax_id = []
        for company_id in self.env['res.company'].sudo().search([]):
            account_sale_tax_id.append(
                company_id.account_sale_tax_id.id
            )
            account_purchase_tax_id.append(
                company_id.account_purchase_tax_id.id
            )
        vals.update(dict(
            taxes_id=[(6, 0, account_sale_tax_id)],
            supplier_taxes_id=[(6, 0, account_purchase_tax_id)]
        ))
        res = super(ProductProduct, self).create(vals)
        return res

    def sltech_update_cost_price_and_tax(self):
        pro_ids = self.search([])
        account_sale_tax_id = []
        account_purchase_tax_id = []
        for pro_id in pro_ids:
            for company_id in self.env['res.company'].sudo().search([]):
                standard_price = pro_id.standard_price
                scsp_obj = self.env['stock.change.standard.price']
                default_values = scsp_obj.sudo().with_context(active_id=pro_id.id,
                                                              active_ids=pro_id.ids,
                                                              active_model='product.product',
                                                              allowed_company_ids=company_id.ids).default_get(scsp_obj._fields.keys())
                default_values.update({
                    'new_price': standard_price
                })
                scsp_id = scsp_obj.with_context(active_id=pro_id.id,
                                                active_ids=pro_id.ids,
                                                active_model='product.product',
                                                allowed_company_ids=company_id.ids).create(default_values)
                scsp_id.with_context(active_id=pro_id.id,
                                     active_ids=pro_id.ids,
                                     active_model='product.product',
                                     allowed_company_ids=company_id.ids).change_price()

                account_sale_tax_id.append(
                    company_id.account_sale_tax_id.id
                )
                account_purchase_tax_id.append(
                    company_id.account_purchase_tax_id.id
                )

            pro_id.sudo().write(dict(
                taxes_id=[(6, 0, account_sale_tax_id)],
                supplier_taxes_id = [(6, 0, account_purchase_tax_id)]
            ))