# -*- coding: utf-8 -*-

from odoo import models, fields


class res_users(models.Model):
    """
    Overwrite to add default warehouse which might be changed in preferences
    """
    _inherit = "res.users"

    default_warehouse = fields.Many2one(
        'stock.warehouse',
        string='Default Warehouse',
    )

    def __init__(self, pool, cr):
        """
        Overwrite to redefine SELF_WRITEABLE_FIELDS in order to let user change their default warehouse
        """
        init_res = super(res_users, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        type(self).SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        type(self).SELF_WRITEABLE_FIELDS.extend(['default_warehouse'])
        # duplicate list to avoid modifying the original reference
        type(self).SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        type(self).SELF_READABLE_FIELDS.extend(['default_warehouse'])
        return init_res
