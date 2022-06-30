# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrContract(models.Model):
    _inherit = 'hr.contract'


    is_notifiy = fields.Boolean(string="Enable Notifications?", default=False, store=True)
    notifiy_type = fields.Selection([
        ('day', 'A day before'),
        ('week', 'A week before'),
        ('month', 'A month before')
    ], string="When to notify?", default='week', store=True)  # TODO: Required whenever notifying is enabled (In view)
    notifiy_date = fields.Date(string="Notification Date", store=True)
    notify_template_id = fields.Many2one('mail.template', string='Email Template',
        domain=[('model', '=', 'event.registration')], required=True, ondelete='restrict',
        help='This field contains the template of the mail that will be automatically sent!')







