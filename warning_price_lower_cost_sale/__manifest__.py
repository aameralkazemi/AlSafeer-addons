# -*- coding: utf-8 -*-
{
    'name': "Warning Price Lower Cost Sale",

    'summary': """
        Give a warning if product price set lower than the product cost
        """,

    'description': """
        On retail store customers can do negotiate the product that they want.
        But sometimes a cashier can do some mistake such change the product price lower than the product cost.
        Using this module we can give an alert like red color on the product order line if cashiers do that mistake.
    """,

    'author': "da Ti Soft Consulting",
    'website': "https://github.com/trinanda/",
    'images': ['static/description/icon.png'],

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Utilities',
    'version': '13.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
