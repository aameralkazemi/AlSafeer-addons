# -*- coding: utf-8 -*-
{
    'name': 'Currency exchange rate Invoice',
    'version': '1.0',
    'category': 'Accounting',
    'author': 'Pragmatic SAS',
    'summary': 'This module allows the use of different types of exchange rates according to your need, the entry of the value of the rate is manually, that is, you enter the value that can be used in this case.',
    'website':'http://www.pragmatic.com.co/',
    'version': '13.0.2.0',
    'license': 'OPL-1',
    'support': 'info@pragmatic.com.co',
    'price': '9.99',
    'currency': 'EUR',
    'images': ['static/description/TRM.jpg'], 
    
    'depends': ['base','account'],
    'data': [
        'views/account_move.xml',
        'views/payment_record.xml',
    ],
}
