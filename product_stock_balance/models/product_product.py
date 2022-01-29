# -*- coding: utf-8 -*-

from odoo import api, fields, models

class product_product(models.Model):
    """
    Overwrite to add methods to calculate locations for this product
    """
    _inherit = 'product.product'

    def _compute_qty_available_total(self):
        """
        Compute method for qty_available_total

        Methods:
         * _product_available - of product.product
        """
        self = self.with_context(total_warehouse=True)
        qtys = self._product_available(["qty_available"], False)
        for product in self:
            total_qty = qtys.get(product.id).get("qty_available")
            product.qty_available_total = total_qty

    qty_available_total = fields.Float(
        "Total Quantity",
        compute=_compute_qty_available_total,   
        help="Quantity on hand without filtering by default user warehouse",    
        digits='Product Unit of Measure',
    )

    def _get_domain_locations(self):
        """
        Overwrite core method to add check of user's default warehouse.

        The goal is to show available quantities only for default user warehouse
        While locations table show all stocks
        """
        def_warehouse = self.env.user.default_warehouse
        if not (self._context.get('warehouse', False) or self._context.get('location', False) \
                or self._context.get("total_warehouse", False)) and def_warehouse:
            res = super(product_product, self.with_context(warehouse=def_warehouse.id))._get_domain_locations()
        else:
            res = super(product_product, self)._get_domain_locations()
        return res

    def action_show_table_sbl(self):
        """
        The method to open the tbale of stocks by locations
        
        Returns:
         * action of opening the table form

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        action_id = self.env.ref("product_stock_balance.product_product_sbl_button_only_action").read()[0]
        action_id["res_id"] = self.id
        return action_id

    def action_prepare_xlsx_balance_product(self):
        """
        To trigger the method of template
        """
        res = self.product_tmpl_id.action_prepare_xlsx_balance()
        return res
