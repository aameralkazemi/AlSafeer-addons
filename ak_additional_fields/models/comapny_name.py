from odoo import models, fields

class productTemplate(models.Model):
    _inherit="res.company"

    name_of_company = fields.Char(string = "Company Name")