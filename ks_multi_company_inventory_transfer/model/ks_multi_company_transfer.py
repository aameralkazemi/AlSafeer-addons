from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class KsStockTransferMultiCompany(models.Model):
    _name = 'multicompany.transfer.stock'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Multi Company Inventory Transfer"

    name = fields.Char(readonly=True, copy=False)
    ks_transfer_to = fields.Many2one('res.company', string='Company To', required=True, domain=lambda self: ['|', ('id', '=', self.env.company.id), ('parent_id', '=', self.env.company.id)], track_visiblity='always')
    ks_transfer_to_location = fields.Many2one('stock.location', string='Destination Location', required=True)
    ks_transfer_from = fields.Many2one('res.company', string='Company From',
                                       default=lambda self: self.env.company,
                                       required=True,
                                       domain=lambda self: ['|', ('id', '=', self.env.company.id), ('parent_id', '=', self.env.company.id)], tracking=True, track_visiblity='always'
                                       )
    ks_transfer_from_location = fields.Many2one('stock.location', string='Source Location', required=True)
    ks_memo_for_transfer = fields.Char('Internal Notes')
    ks_schedule_date = fields.Datetime('Schedule Date', default=lambda *a: fields.Datetime.now(), required=True,tracking=True)
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft',tracking=True)
    ks_multicompany_transfer_stock_ids = fields.One2many('multicompany.transfer.stock.line',
                                                         'ks_multicompany_transfer_id')
    ks_stock_picking_ids = fields.Many2many('stock.picking')

    @api.onchange('ks_transfer_to')
    def ks_set_payment_to_account(self):
        self.ks_transfer_to_account = False

    def ks_confirm_inventory_transfer(self):
        move_lines = [(0, 0, {
            'name': i.ks_product_id.name,
            'product_id': i.ks_product_id.id,
            'quantity_done': i.ks_qty_transfer,
            'product_uom_qty': i.ks_qty_transfer,
            'product_uom': i.ks_product_uom_type.id
        }) for i in self.ks_multicompany_transfer_stock_ids]
        self.name = self.env['ir.sequence'].with_context(ir_sequence_date=self.ks_schedule_date). \
            next_by_code("multicompany.transfer.inventory")
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'outgoing'),
            ('warehouse_id.company_id', '=', self.ks_transfer_from.id),
        ], limit=1)
        if not picking_type:
            raise ValidationError("Outgoing Picking is not defined for %s" % (self.ks_transfer_from.name))
        ks_picking_from_id = self.env['stock.picking'].create({
            'picking_type_id': picking_type.id,
            'location_id': self.ks_transfer_from_location.id,
            'partner_id': self.ks_transfer_to.partner_id.id,
            'scheduled_date': self.ks_schedule_date,
            'move_lines': move_lines,
            'origin': self.name,
            'location_dest_id': self.env['stock.location'].search([('usage', '=', 'customer'), '|',
                                                                   ('company_id', '=', self.ks_transfer_from.id),
                                                                   ('company_id', '=', False),

                                                                   ], limit=1, order='company_id desc').id,
        })
        ks_picking_from_id.button_validate()
        picking_incoming_id = self.env['stock.picking.type'].search([
            ('code', '=', 'incoming'),
            ('warehouse_id.company_id', '=', self.ks_transfer_to.id),
        ], limit=1)
        if not picking_incoming_id:
            raise ValidationError("Incoming Picking is not defined for %s" % (self.ks_transfer_to.name))
        ks_picking_to_id = self.env['stock.picking'].create({
            'picking_type_id': picking_incoming_id.id,
            'location_id': self.env['stock.location'].search([('usage', '=', 'supplier'), '|',
                                                              ('company_id', '=', self.ks_transfer_to.id),
                                                              ('company_id', '=', False)
                                                              ], limit=1, order='company_id desc').id,
            'partner_id': self.ks_transfer_from.partner_id.id,
            'scheduled_date': self.ks_schedule_date,
            'move_lines': move_lines,
            'origin': self.name,
            'location_dest_id': self.ks_transfer_to_location.id
        })
        ks_picking_to_id.button_validate()
        self.state = 'posted'
        self.ks_stock_picking_ids = [(6, 0, [ks_picking_from_id.id, ks_picking_to_id.id])]

    def ks_button_inventory_entries(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Inventory Transfer',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.ks_stock_picking_ids.ids)],
            'view_type': 'form',
            'target': 'current',
        }


class KsStockTransferMultiCompanyLines(models.Model):
    _name = 'multicompany.transfer.stock.line'
    _description = "Multi Company Inventory Transfer"

    ks_product_id = fields.Many2one('product.product', string="Product", required=True)
    ks_multicompany_transfer_id = fields.Many2one('multicompany.transfer.stock')
    ks_qty_avalaible = fields.Float('Qty available', compute="get_location_quantity")
    ks_qty_transfer = fields.Float('Qty to Transfer', required=True)
    ks_product_uom_type = fields.Many2one('uom.uom', string='Unit of measurement', related='ks_product_id.uom_id',
                                          required=True, store=True
                                          )

    # @api.multi
    @api.depends('ks_product_id', 'ks_multicompany_transfer_id.ks_transfer_from_location')
    def get_location_quantity(self):
        for rec in self:
            if rec.ks_multicompany_transfer_id.ks_transfer_from_location:
                rec.ks_qty_avalaible = rec.env['stock.quant'].search(
                    [('location_id', '=', rec.ks_multicompany_transfer_id.ks_transfer_from_location.id),
                     ('company_id', '=', rec.ks_multicompany_transfer_id.ks_transfer_from.id),
                     ('product_id', '=', rec.ks_product_id.id)], limit=1).quantity


class KsCustomModule(models.TransientModel):
    _inherit = 'res.config.settings'

    module_ks_inventory_transfer_custom = fields.Boolean('Inventory Transfer Custom module')
    is_module_install = fields.Boolean('is module install', default='_auto_hide')

    def _auto_hide(self):
        for rec in self:
            module_status = rec.env['ir.module.module'].search([('name','=','ks_inventory_transfer_custom')])
            if module_status:
                return True
            else:
                return False