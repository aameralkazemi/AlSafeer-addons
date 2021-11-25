# -*- coding: utf-8 -*-
##############################################################################
#
#    SLTECH ERP SOLUTION
#    Copyright (C) 2020-Today(www.slecherpsolution.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Accounting',
    'category': 'Accounting/Accounting',
    'summary': 'Manage financial and analytic accounting',
    'description': """
Accounting Access Rights
========================
It gives the Administrator user access to all accounting features such as journal items and the chart of accounts.

It assigns manager and user access rights to the Administrator for the accounting application and only user rights to the Demo user.
""",
    'website': 'https://www.sltecherpsolution.com',
    'depends': ['account', 'web_tour'],
    'data': [
        'data/account_accountant_data.xml',
        'data/digest_data.xml',
        'security/account_accountant_security.xml',
        'views/account_accountant_templates.xml',
        'views/account_move_views.xml',
        'views/digest_views.xml',
        'views/res_config_settings_views.xml',
        'views/product_views.xml',
        'wizard/account_change_lock_date.xml',
    ],

}
