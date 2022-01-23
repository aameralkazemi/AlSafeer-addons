
{
    'name': "Additonal fields for yeslam",
    'version': "13.0.0.0",
    'summary': "additional fields",
    'category': 'Extra Addons',
    'description': """
        this app will add alternative name and code to partners
        and Reference,Barcode, and HS Code to Products
    """,
    'author': "Expertsintech",
    'website':"www.expertsintech.com",
    'depends': ['base','stock','sale'],
    'data': [
    'views/altNameView.xml',
    'views/productTemplateView.xml',
    'views/customer_search.xml',
    'views/qty_on_hand.xml',
    "views/company_view.xml",




    ],
    'demo': [],
    "external_dependencies": {},
    "license": "AGPL-3",
    'installable': True,
    'auto_install': False,

}
