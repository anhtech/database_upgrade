# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    zip = fields.Char(change_default=True, string="Block")
    street = fields.Char(string="Road")
    street2 = fields.Char(string="House")