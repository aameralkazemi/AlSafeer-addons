# -*- coding: utf-8 -*-
# from odoo import http


# class WarningPriceBelowCostSale(http.Controller):
#     @http.route('/warning_price_lower_cost_sale/warning_price_lower_cost_sale/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/warning_price_lower_cost_sale/warning_price_lower_cost_sale/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('warning_price_lower_cost_sale.listing', {
#             'root': '/warning_price_lower_cost_sale/warning_price_lower_cost_sale',
#             'objects': http.request.env['warning_price_lower_cost_sale.warning_price_lower_cost_sale'].search([]),
#         })

#     @http.route('/warning_price_lower_cost_sale/warning_price_lower_cost_sale/objects/<model("warning_price_lower_cost_sale.warning_price_lower_cost_sale"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('warning_price_lower_cost_sale.object', {
#             'object': obj
#         })
