from odoo import models
import base64
import io
import logging
import requests
import werkzeug.utils

from PIL import Image
from odoo import http, tools, _
from odoo.http import request
from werkzeug.urls import url_encode
import json
from odoo import models, tools, fields, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime, date, timedelta

class AccountMoveLineReport(models.TransientModel):
    _name = "sltech.acc.move.line.report"

    name = fields.Char()
    from_date = fields.Date('From date')
    to_date = fields.Date('To date')
    product_ids = fields.Many2many('product.product', string='Products')
    partner_ids = fields.Many2many('res.partner', string='Customers')

    def generate_report_xlsx(self):
        return dict(
            report_name='sltech_account_move_line_report.acc_mv_line_report_name',
            report_type='xlsx',
            type='ir.actions.report',
        )

class SLtechAccountMoveLineXLSXReport(models.AbstractModel):
    _name = 'report.sltech_account_move_line_report.acc_mv_line_report_name'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        if obj:
            company_ids = []
            if data.get('data'):
                data_context = json.loads(data['data'])

                json.loads(data['data'])[2][0]['allowed_company_ids']

                if data_context and len(data_context) > 1 and len(data_context[2]) > 0 and data_context[2][0].get('allowed_company_ids'):
                    company_ids = data_context[2][0].get('allowed_company_ids')

            acc_move_ids = self.env['account.move'].search([('type', 'in', ['out_invoice',
                                                                                 'out_refund',
                                                                                 'in_refund',
                                                                                 'in_invoice']),
                                                            ('company_id', 'in', company_ids),
                                                            ('invoice_date', '>=', str(obj.from_date)),
                                                            ('invoice_date', '<=', str(obj.to_date))])
            acc_move_line_ids = []
            if acc_move_ids:
                if obj.partner_ids:
                    acc_move_ids = acc_move_ids.filtered(lambda x: x.partner_id.id in obj.partner_ids.ids)
                if acc_move_ids:
                    acc_move_line_ids = acc_move_ids.mapped('invoice_line_ids')
                    if acc_move_line_ids:
                        if obj.product_ids:
                            acc_move_line_ids = acc_move_line_ids.filtered(
                                lambda line: line.product_id.id in obj.product_ids.ids)

            worksheet = workbook.add_worksheet('Report')

            worksheet.set_column('A:A', 10)
            worksheet.set_column('B:B', 15)
            worksheet.set_column('C:C', 10)
            worksheet.set_column('D:D', 20)
            worksheet.set_column('E:E', 8)
            worksheet.set_column('F:F', 8)
            worksheet.set_column('G:G', 12)
            worksheet.set_column('H:H', 8)
            worksheet.set_column('I:I', 10)
            # worksheet.set_column('J:J', 10)

            row=1

            merge_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': 1, })
            worksheet.write('A1', 'invoice number', merge_format)
            worksheet.write('B1', 'invoice number', merge_format)
            worksheet.write('C1', 'client name', merge_format)
            worksheet.write('D1', 'product name', merge_format)
            worksheet.write('E1', 'product internal reference', merge_format)
            worksheet.write('F1', 'quantity', merge_format)
            worksheet.write('G1', 'sale price', merge_format)
            worksheet.write('H1', 'total', merge_format)
            worksheet.write('I1', 'saleperson name', merge_format)

            row+=1
            col = workbook.add_format({'align': 'center', 'valign': 'vcenter',})
            # states = ''
            # if acc_move_line_ids:
            #     states = [res for res in ticket_inv_line_ids[0].helpdesk_inv_ids._fields['state'].selection]        # if state == res[0]][0][1]

            for inv_line in acc_move_line_ids:
                worksheet.write(('A%s' % (str(row))), inv_line.move_id.name, col)
                worksheet.write(('B%s' % (str(row))), inv_line.move_id.invoice_date, col)
                worksheet.write(('C%s' % (str(row))), inv_line.move_id.partner_id.name, col)
                worksheet.write(('D%s' % (str(row))), inv_line.product_id.name, col)
                worksheet.write(('E%s' % (str(row))), inv_line.product_id.default_code, col)
                worksheet.write(('F%s' % (str(row))), inv_line.quantity, col)
                worksheet.write(('G%s' % (str(row))), inv_line.price_unit, col)
                worksheet.write(('H%s' % (str(row))), inv_line.price_subtotal, col)
                worksheet.write(('I%s' % (str(row))), inv_line.move_id.user_id.name or '', col)

                row += 1