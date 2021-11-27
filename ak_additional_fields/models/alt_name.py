from odoo import models, api, _, _lt, fields

class Partnerpage(models.Model):
    _inherit = 'res.partner'

    altName = fields.Char(string="English Name")
    partnerCode = fields.Char(string="Partner Code" , index = True , store = True)





class drivername(models.Model):
    _inherit= 'stock.picking'
    driver_name = fields.Char(string= "Driver Name")

