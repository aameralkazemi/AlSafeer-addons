# -*- coding: utf-8 -*-

from odoo import api, models


class ProductReplenish(models.TransientModel):
    _inherit = 'product.replenish'

    @api.model
    def default_get(self, fields):
        """
        Re-write to take user default warehouse
        """
        res = super(ProductReplenish, self).default_get(fields)
        if self.env.user.default_warehouse:
            res['warehouse_id'] = self.env.user.default_warehouse.id
        return res
