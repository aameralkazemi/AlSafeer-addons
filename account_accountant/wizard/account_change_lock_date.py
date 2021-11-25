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
from odoo import models, fields, api

class AccountChangeLockDate(models.TransientModel):
    """
    This wizard is used to change the lock date
    """
    _name = 'account.change.lock.date'
    _description = 'Change Lock Date'

    period_lock_date = fields.Date(
        string='Lock Date for Non-Advisers',
        default=lambda self: self.env.company.period_lock_date,
        help='Only users with the Adviser role can edit accounts prior to and inclusive of this date. Use it for period locking inside an open fiscal year, for example.')
    fiscalyear_lock_date = fields.Date(
        string='Lock Date for All Users',
        default=lambda self: self.env.company.fiscalyear_lock_date,
        help='No users, including Advisers, can edit accounts prior to and inclusive of this date. Use it for fiscal year locking for example.')
    tax_lock_date = fields.Date(
        "Tax Lock Date",
        default=lambda self: self.env.company.tax_lock_date,
        help='No users can edit journal entries related to a tax prior and inclusive of this date.')


    def change_lock_date(self):
        self.env.company.write({'period_lock_date': self.period_lock_date,
                                        'fiscalyear_lock_date': self.fiscalyear_lock_date,
                                        'tax_lock_date': self.tax_lock_date,
                                        })
        return {'type': 'ir.actions.act_window_close'}
