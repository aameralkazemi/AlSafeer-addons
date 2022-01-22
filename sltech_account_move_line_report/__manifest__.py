# -*- coding: utf-8 -*-
{
    'name': "Account Move Line Report",
    'author': "Sachin Burnawal",
    'website': "https://www.sltecherpsolution.com",
    'category': 'Account',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base','account','report_xlsx'],
    # always loaded
    'data': [
            'views/ticket.xml',
            'views/service_ticket_report.xml',
    ],
}