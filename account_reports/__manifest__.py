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
    'name' : 'Accounting Reports',
    'summary': 'View and create reports',
    'category': 'Accounting/Accounting',
    'description': """
Accounting Reports
==================
    """,
    'depends': ['account_accountant'],
    'website': 'https://www.sltecherpsolution.com',
    'data': [
        'security/ir.model.access.csv',
        'data/account_financial_report_data.xml',
        'views/assets.xml',
        'views/account_report_view.xml',
        'views/report_financial.xml',
        'views/search_template_view.xml',
        'views/partner_view.xml',
        'views/account_journal_dashboard_view.xml',
        'views/res_config_settings_views.xml',
        'wizard/report_export_wizard.xml',
        'wizard/fiscal_year.xml',
        'views/account_activity.xml',
    ],
    'qweb': [
        'static/src/xml/account_report_template.xml',
    ],
    'post_init_hook': 'set_periodicity_journal_on_companies',
}
