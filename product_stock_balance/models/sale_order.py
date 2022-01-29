# -*- coding: utf-8 -*-

from odoo import api, models


class sale_order(models.Model):
    """
    Overwrite to add default warehouse logic
    """
    _inherit = "sale.order"

    @api.onchange('user_id')
    def onchange_user_id(self):
        """
        Onchange method for user_id

        Attr update:
         * warehouse_id - as default user warehouse
        """
        for order in self:
            if order.user_id and order.user_id.default_warehouse:
                order.warehouse_id = order.user_id.default_warehouse

    @api.onchange('company_id')
    def _onchange_company_id(self):
        """
        Re-write to trigger user change after company change
        """
        super(sale_order, self)._onchange_company_id()
        self.onchange_user_id()
