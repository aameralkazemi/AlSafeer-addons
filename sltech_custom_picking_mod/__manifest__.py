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
    'name': 'One Step to put done quantities',
    'version': '1.0',
    'category': 'One Step to put done quantities',
    'summary': 'When multiWarehouses are enabled you can put done in quantities in main page ',
    'description': "",
    'author': "Sachin Burnawal",
    'website': 'https://www.sltecherpsolution.com/',
    'license': 'Other proprietary',
    'depends': [
        'stock',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/product_template.xml',
        'views/stock_picking.xml',
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'css': [
    ],
}
