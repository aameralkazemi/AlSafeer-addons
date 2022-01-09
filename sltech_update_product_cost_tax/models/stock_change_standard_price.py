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
from odoo import api, fields, models

class StockChangeStandardPrice(models.TransientModel):
    _inherit = "stock.change.standard.price"
    _description = "Change Standard Price"

    def change_price(self):
        """ Changes the Standard Price of Product and creates an account move accordingly. """
        res = super(StockChangeStandardPrice, self).change_price()

        if not self._context.get('sltech_stop'):
            context_model = self._context['active_model']

            pro_id = self.env[context_model].browse(self._context['active_id'])
            for company_id in self.env['res.company'].sudo().search([]):
                standard_price = self.new_price
                scsp_obj = self.env['stock.change.standard.price']

                default_values = scsp_obj.sudo().with_context(active_id=pro_id.id,
                                                              active_ids=pro_id.ids,
                                                              active_model=context_model,
                                                              allowed_company_ids=company_id.ids).default_get(
                    scsp_obj._fields.keys())
                default_values.update({
                    'new_price': standard_price
                })
                scsp_id = scsp_obj.with_context(active_id=pro_id.id,
                                                active_ids=pro_id.ids,
                                                active_model=context_model,
                                                allowed_company_ids=company_id.ids).create(default_values)
                scsp_id.with_context(active_id=pro_id.id,
                                     active_ids=pro_id.ids,
                                     sltech_stop=True,
                                     active_model=context_model,
                                     allowed_company_ids=company_id.ids).change_price()

        return res
