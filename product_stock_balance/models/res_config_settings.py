# -*- coding: utf-8 -*-

from odoo import fields, models


class res_config_settings(models.TransientModel):
    """
    The model to keep settings of stocks' aizard
    """
    _inherit = "res.config.settings"

    group_stocks_show_only_by_button = fields.Boolean(
        "Stocks by locations: button only", 
        implied_group='product_stock_balance.group_stocks_show_only_by_button',
    ) 
    product_stock_balance_default_levels = fields.Integer(
    	"Default Levels Expanded",
    	config_parameter='product_stock_balance_default_levels',
        default=3,
    )

