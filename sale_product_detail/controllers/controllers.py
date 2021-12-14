# -*- coding: utf-8 -*-
# from odoo import http


# class SaleProductDetail(http.Controller):
#     @http.route('/sale_product_detail/sale_product_detail/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_product_detail/sale_product_detail/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_product_detail.listing', {
#             'root': '/sale_product_detail/sale_product_detail',
#             'objects': http.request.env['sale_product_detail.sale_product_detail'].search([]),
#         })

#     @http.route('/sale_product_detail/sale_product_detail/objects/<model("sale_product_detail.sale_product_detail"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_product_detail.object', {
#             'object': obj
#         })
