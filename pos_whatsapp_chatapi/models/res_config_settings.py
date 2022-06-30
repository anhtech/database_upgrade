# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    chat_api_enabled = fields.Boolean(string='Enable Automatic Whatsapp Messaging', default=False, config_parameter='pos_whatsapp_chatapi.chat_api_enabled')
    chat_api_url = fields.Char(string='API URL', config_parameter='pos_whatsapp_chatapi.chat_api_url')
    chat_api_token = fields.Char(string='API TOKEN', config_parameter='pos_whatsapp_chatapi.chat_api_token')
    chat_api_success = fields.Boolean(default=False, config_parameter='pos_whatsapp_chatapi.chat_api_success')
    chat_api_message_template = fields.Char(string='Message Template', default="Thank you for shopping with us 👋,\nthis is a short summary of your order:\n\n<ordered_products>\n\nTotal Quantity: <total_qty>\nSubtotal: <subtotal>\nVAT: <vat>\n*Total: <total>*\n\nPlease find below a copy of your receipt 👇"
                                            , help="Use the following codes in your template to show them where ever you want: "
                                                  "\nList of Products: <ordered_products>"
                                                  "\nTotal Quantity: <total_qty>"
                                                  "\nSubtotal: <subtotal>"
                                                  "\nVAT: <vat>"
                                                  "\nTotal: <total>"
                                                   "\nNew Line: \ n (With Space)",
                                            config_parameter='pos_whatsapp_chatapi.chat_api_message_template')

    @api.onchange('chat_api_enabled')
    def onChatAPIDisabled(self):
        if self.chat_api_enabled == False:
            self.chat_api_url = False
            self.chat_api_token = False
            self.chat_api_success = False

    @api.onchange('chat_api_url', 'chat_api_token')
    def onChatAPIChanged(self):
        self.chat_api_success = False

    @api.one
    def checkChatAPIConnection(self):
        if not self.chat_api_enabled:
            raise UserError(_('You can not check the connection while the Chat API is disabled!'))
        if not self.chat_api_url:
            raise UserError(_('You need to enter the Chat API URL!'))
        if not self.chat_api_token:
            raise UserError(_('You need to enter the Chat API Token!'))
        check_status_url = str(self.chat_api_url)+"/status?token="+self.chat_api_token
        r = requests.get(check_status_url)
        if r.status_code != 200:
            raise UserError(_("There was a problem while connecting to the API! (ERROR CODE: %s)" % (str(r.status_code),)))
        data = r.json()
        if 'accountStatus' in data:
            if data['accountStatus'] == "loading":
                self.chat_api_success = False
                raise UserError(_("Someone opened the whatsapp web on another device!"))
            if data['accountStatus'] == "init":
                self.chat_api_success = False
                raise UserError(_("The Whatsapp API is still not initialized!"))
            if data['accountStatus'] == "got qr code":
                self.chat_api_success = False
                raise UserError(_("You need to link your whatsapp to the API before using it!"))
            if data['accountStatus'] == "authenticated":
                self.chat_api_success = True
                self.env.user.notify_success(message='Connection Success!')
        else:
            self.chat_api_success = False
            raise UserError(_("Unknown Error!"))

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            chat_api_url=ICPSudo.get_param('pos_whatsapp_chatapi.chat_api_url'),
            chat_api_enabled=ICPSudo.get_param('pos_whatsapp_chatapi.chat_api_enabled'),
            chat_api_success=ICPSudo.get_param('pos_whatsapp_chatapi.chat_api_success'),
            chat_api_message_template=ICPSudo.get_param('pos_whatsapp_chatapi.chat_api_message_template'),
        )
        return res
