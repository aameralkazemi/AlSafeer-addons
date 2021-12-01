from odoo import models, fields

class productTemplate(models.Model):
    _inherit="product.template"
    englishName = fields.Char(string="English Name")
    description2 = fields.Char(string="Item Description")
    additional_sale_price = fields.Float(string = "Sales Price 2")
