# -*- coding: utf-8 -*-

from odoo import models, fields


class SalesPerson(models.Model):
    _name = 'sales.person'
    _description = 'Sales Person'

    name = fields.Char(string="Salesperson", store=True)
