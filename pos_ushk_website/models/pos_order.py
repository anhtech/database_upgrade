# -*- coding: utf-8 -*-

from odoo import models, fields, api

class posOrder(models.Model):
    _inherit = 'pos.order'

    ushk_ref = fields.Char('Ushk Website Reference')
