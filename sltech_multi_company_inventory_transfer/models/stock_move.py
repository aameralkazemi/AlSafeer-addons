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
from odoo.exceptions import UserError, ValidationError

class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id, description):
        """
        Generate the account.move.line values to post to track the stock valuation difference due to the
        processing of the given quant.
        """
        res = super(StockMove, self)._prepare_account_move_line(qty=qty, cost=cost, credit_account_id=credit_account_id, debit_account_id=debit_account_id, description=description)

        if self._context.get('sltech_change_account'):
            sltech_res = []
            sltech_from_check = False
            sltech_to_check = False
            for r in res:
                product_id = self.env['product.product'].browse(r[2]['product_id'])

                if self._context.get('from_partner_id') == r[2]['partner_id']:
                    if r[2]['account_id'] == product_id.with_context(allowed_company_ids=
                                                                     [self._context.get(
                                                                         'from_company_id')]).categ_id.with_context(
                        allowed_company_ids=
                        [self._context.get('from_company_id')]).property_stock_valuation_account_id.id:
                        sltech_from_check = True
                if self._context.get('to_partner_id') == r[2]['partner_id']:
                    if r[2]['account_id'] == product_id.with_context(allowed_company_ids=
                                                                     [self._context.get('to_company_id')]).categ_id.with_context(allowed_company_ids=
                                                                     [self._context.get('to_company_id')]).property_stock_valuation_account_id.id:
                        sltech_to_check = True
            for r in res:
                if sltech_from_check:
                    if r[2]['credit'] > 0:
                        partner_id = self.env['res.partner'].browse(r[2]['partner_id'])
                        r[2]['account_id'] = partner_id.intermediary_account_id.id
                if sltech_to_check:
                    if r[2]['debit'] > 0:
                        partner_id = self.env['res.partner'].browse(r[2]['partner_id'])
                        r[2]['account_id'] = partner_id.intermediary_account_id.id
                sltech_res.append(r)


            return sltech_res

        return res