from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = "product.product"

    sale_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)