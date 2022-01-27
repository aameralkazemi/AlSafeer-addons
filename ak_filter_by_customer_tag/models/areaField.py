from odoo import models, fields


class areaPartner(models.Model):
    _inherit = 'res.partner'

  

    area = fields.Char(string = "Customer type", store=True )


class areaSales(models.Model):
    _inherit = 'sale.order'

    area = fields.Char(string = "Customer type", readonly=True,store=True, related="partner_id.area")





class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    area = fields.Char(string="Customer type", readonly=True)

    def _select(self):
        return super(PurchaseReport, self)._select() + ", partner.area as area"

    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + ", partner.area"



class areaPurhcases(models.Model):
    _inherit = 'purchase.order'

    area = fields.Char(string = "Customer type", store = 'true', readonly=True, related="partner_id.area")


class SaleReport(models.Model):
    _inherit = "sale.report"

    area = fields.Char(string="Customer type", readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['area'] = ", partner.area as area"
        groupby += ", partner.area"
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)


#
# class SaleReport(models.Model):
#     _inherit = "sale.report"
#
#     area = fields.Char(string="Area", readonly=True)
#
#     def _select(self):
#         return super(SaleReport, self)._select() + ", s.area as area"
#
#     def _group_by(self):
#         return super(SaleReport, self)._group_by() + ", s.area"

