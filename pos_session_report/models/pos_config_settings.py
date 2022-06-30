# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _

class pos_config_settings(models.Model):
    _inherit = 'pos.config'

    branch_name = fields.Char("Branch Name", default="Enter your branch name", store=True)

