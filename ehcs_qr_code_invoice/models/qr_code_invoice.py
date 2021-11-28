# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request
from odoo.addons.ehcs_qr_code_base.models.qr_code_base import generate_qr_code
from odoo.addons.ehcs_qr_code_base.models.QR_Encoder import Fatoora
from datetime import datetime, timedelta


class QRCodeInvoice(models.Model):
    _inherit = 'account.move'

    qr_image = fields.Binary("QR Code", compute='_generate_qr_code' )
    qr_in_report = fields.Boolean('Show QR in Report')


    @api.depends()
    def _generate_qr_code(self):

        if self.invoice_date:
            current_date = self.invoice_date
            future_date_and_time = current_date + timedelta(hours=3)

            fatoora_obj = Fatoora(
                seller_name=self.company_id.name,
                tax_number=self.company_id.vat,  # or "1234567891"
                invoice_date=str(future_date_and_time),  # Timestamp
                total_amount= self.amount_total,  # or 100.0, 100.00, "100.0", "100.00"
                tax_amount= self.amount_tax,  # or 15.0, 15.00, "15.0", "15.00"
            )

            print("----------------------------------------------")
            print("----------------------------------------------")
            print(fatoora_obj.base64)

            base_url = fatoora_obj.base64

            self.qr_image = generate_qr_code(base_url)

            return self.qr_image

