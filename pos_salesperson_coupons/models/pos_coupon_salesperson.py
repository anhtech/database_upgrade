# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PosCouponSalesperson(models.Model):
    _name = 'pos.coupon.salesperson'
    _description = 'Coupon'
    _rec_name = 'ref'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id, readonly=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id, readonly=True)

    ref = fields.Char(string="Coupon Code", required=True)
    salesperson_id = fields.Many2one('sales.person', "Salesperson")
    salesperson_commission = fields.Float('Salesperson Commission (%)', default=0)  # TODO: Required when salesperson_id != False
    number_of_used = fields.Integer(default=0, required=True)
    number_of_available = fields.Integer(string="Allowed to be used for (n Times)", default=1, required=True)
    remaining_to_use = fields.Integer(compute='_computeRemainingUses')
    valid_til = fields.Date(string="Validity", help="If you left this field as empty, the coupon will be valid forever.")
    is_discount_products = fields.Boolean("Discount on Products?", default=False)
    is_discount_on_all_products = fields.Boolean("Discount on All Products?", default=False)
    discount_all_products_per = fields.Float("Discount (%)", default=0)
    product_lines = fields.One2many('coupon.product.line', 'coupon_id', string='Coupon Products')
    is_discount_value = fields.Boolean("Discount Value?", default=False)
    discount_value = fields.Monetary("Discount Amount", default=0, required=True, currency_field='currency_id')

    _sql_constraints = [
        ('discount_amount_check', 'CHECK (discount_value >= 0)', 'Discount value can not be less than 0!'),
        ('unique_coupon_code', 'unique (ref)', 'The coupon code should be unique !'),
    ]

    def getCoupons(self):
        return self.env['pos.coupon.salesperson'].search([('remaining_to_use', '>', 0)])

    @api.multi
    @api.depends('number_of_used', 'number_of_available')
    def _computeRemainingUses(self):
        for record in self:
            diff = record.number_of_available-record.number_of_used
            # if diff < 0:
            #     raise UserError(_('The number of available uses for the coupon can not be in negative!'))
            record.remaining_to_use = diff

    @api.onchange('is_discount_on_all_products')
    def _onDiscountAllProductsChanged(self):
        self.is_discount_products = self.is_discount_on_all_products

    @api.onchange('is_discount_products')
    def _onDiscountProductsChanged(self):
        if not self.is_discount_products:
            for product_line in self.product_lines:
                product_line.unlink()

    @api.onchange('product_lines')
    def _onCouponProductsChanged(self):
        if self.product_lines:
            product_ids = []
            for product_line in self.product_lines:
                if product_line.product_id.id in product_ids:
                    raise UserError(_('You can not add two times the same product!'))
                product_ids.append(product_line.product_id.id)
