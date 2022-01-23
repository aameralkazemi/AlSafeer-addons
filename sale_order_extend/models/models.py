# -*- coding: utf-8 -*-

from odoo import models, fields, api
class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            args = args if args else []
            args.extend([['englishName', 'ilike', name]])
            name = ''
        return super(ProductProductInherit, self).name_search(name, args, operator=operator, limit=limit)

