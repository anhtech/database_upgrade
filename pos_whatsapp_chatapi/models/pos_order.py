# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_round
import time
import requests
import base64
import json
import urllib3

SEND_MESSAGE = "/sendMessage"
SEND_FILE = "/sendFile"
TAKE_OVER = "/takeover"

class PosOrder(models.Model):
    _inherit = 'pos.order'

    def takeOverRequest(self, chat_api_url, chat_api_token):
        r = requests.post(str(chat_api_url)+""+TAKE_OVER+"?token="+str(chat_api_token), json={})
        if r.status_code != 200:
            return False
        else:
            data = r.json()
            if 'result' in data:
                if data['result'] == "Takeover request sent to WhatsApp":
                    return True
            return False

    @api.one
    def checkChatAPIConnection(self, chat_api_url, chat_api_token, takeover=True):
        if not chat_api_url:
            return False
        if not chat_api_token:
            return False
        check_status_url = str(chat_api_url)+"/status?token="+str(chat_api_token)
        r = requests.get(check_status_url)
        if r.status_code != 200:
            return False
        data = r.json()
        if 'accountStatus' in data:
            if data['accountStatus'] == "loading":
                if takeover:
                    if self.takeOverRequest(chat_api_url, chat_api_token):
                        return self.checkChatAPIConnection(chat_api_url, chat_api_token, takeover=False)
                return False
            if data['accountStatus'] == "init":
                return False
            if data['accountStatus'] == "got qr code":
                return False
            if data['accountStatus'] == "authenticated":
                return True
        else:
            return False

    @api.one
    def prepareWhatsappTemplate(self, template):
        if not template:
            return False
        # Find the currency:
        currency_id = self.env.user.company_id.currency_id
        if '<ordered_products>' in template:
            products_str = ""
            counter = 1
            for line in self.lines:
                if products_str != "":
                    products_str += "\n"
                products_str += " %s. %s - Qty: %s - Unit Price: %.3f %s" % (str(counter), str(line.product_id.name), str(line.qty), line.price_unit, currency_id.symbol,)
                if line.discount > 0:
                    products_str += " - Discount: %s" % (str(line.discount),)
                    products_str += "%"
                products_str += " - Total: %.3f %s" % (line.price_subtotal_incl, currency_id.symbol,)
                counter += 1
            products_str += "\n"
            template = template.replace("<ordered_products>", products_str)
        if '<total_qty>' in template:
            total_quantity = 0
            for line in self.lines:
                total_quantity += line.qty
            template = template.replace("<total_qty>", str(total_quantity))
        if '<subtotal>' in template:
            template = template.replace("<subtotal>", "%.3f %s" % (self.amount_total-self.amount_tax, currency_id.symbol,))
        if '<vat>' in template:
            template = template.replace("<vat>", "%.3f %s" % (self.amount_tax, currency_id.symbol,))
        if '<total>' in template:
            template = template.replace("<total>", "%.3f %s" % (self.amount_total, currency_id.symbol,))
        template = template.replace("\ n", "\n")
        return template

    @api.one
    def checkIntegerPosibility(self, phone_str):
        try:
            phone = int(phone_str)
            return phone
        except:
            return False

    @api.one
    def prepareCustomerPhoneNumber(self, partner_id):
        phone = partner_id.phone
        if not phone:
            phone = partner_id.mobile
        if not phone:
            return False
        if "973" in phone:
            return self.checkIntegerPosibility(phone)
        if len(phone) == 8:
            return self.checkIntegerPosibility("973"+phone)
        else:
            # The phone number is not a Bahrain phone number.
            # Give it a try and send a whatsapp message
            return self.checkIntegerPosibility(phone)

    @api.one
    def sendManualWhatsappMessage(self):
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_('There is no customer selected for this POS Order!'))
        phone = self.prepareCustomerPhoneNumber(self.partner_id)
        if not phone:
            raise UserError(_('There is no phone number assigned to the customer!'))
        template = self.prepareWhatsappTemplate(self.env['ir.config_parameter'].sudo().get_param('pos_whatsapp_chatapi.chat_api_message_template'))
        if not template:
            raise UserError(_('There is message template, please contact the system administrator!'))
        is_send_enabled = self.env['ir.config_parameter'].sudo().get_param('pos_whatsapp_chatapi.chat_api_enabled')
        chat_api_url = self.env['ir.config_parameter'].sudo().get_param('pos_whatsapp_chatapi.chat_api_url')
        chat_api_token = self.env['ir.config_parameter'].sudo().get_param('pos_whatsapp_chatapi.chat_api_token')
        if not is_send_enabled:
            raise UserError(_('The sending of Whatsapp message is not enable!'))
        is_success = self.env['ir.config_parameter'].sudo().get_param('pos_whatsapp_chatapi.chat_api_success')
        if not is_success:
            new_is_success = self.checkChatAPIConnection(chat_api_url, chat_api_token)
            if not new_is_success:
                raise UserError(_("Error while sending a whatsapp message on order#: %s" % (str(self.name),)))
        # In case the whatsapp is already opened on another device.
        self.takeOverRequest(chat_api_url, chat_api_token)
        # FIXME: I forced the arabic template to be here.
        template = "شكراً لكونكم جزءاً من عائلة عشق ❤ \n\n ستجدون رصيد الشراء مرفق بالأسفل"
        requests.post(str(chat_api_url) + "" + SEND_MESSAGE + "?token=" + str(chat_api_token), data={"phone": phone, "body": template})
        data, data_format = self.env.ref('pos_order_print.pos_order_receipt_pdf').render(self.ids)
        base64_string = base64.urlsafe_b64encode(data).decode('ascii')
        encoded_body = json.dumps({'phone': phone, 'body': "data:application/pdf;base64," + base64_string, 'filename': str(self.pos_reference) + ".pdf"})
        http = urllib3.PoolManager()
        http.request('POST', str(chat_api_url) + "" + SEND_FILE + "?token=" + str(chat_api_token), headers={'Content-Type': 'application/json'}, body=encoded_body)
        self.env.user.notify_success(message='The whatsapp message has been sent successfully!')

    @api.multi
    def write(self, vals):
        res = super(PosOrder, self).write(vals)
        if 'state' in vals:  # When the payments are updated!
            if vals['state'] == 'paid':
                for record in self:
                    if record.partner_id:
                        phone = record.prepareCustomerPhoneNumber(record.partner_id)
                        if phone:
                            template = record.prepareWhatsappTemplate(record.env['ir.config_parameter'].sudo().get_param('pos_whatsapp_chatapi.chat_api_message_template'))
                            if template:
                                is_send_enabled = record.env['ir.config_parameter'].sudo().get_param('pos_whatsapp_chatapi.chat_api_enabled')
                                chat_api_url = record.env['ir.config_parameter'].sudo().get_param('pos_whatsapp_chatapi.chat_api_url')
                                chat_api_token = record.env['ir.config_parameter'].sudo().get_param('pos_whatsapp_chatapi.chat_api_token')
                                if is_send_enabled:
                                    is_success = record.env['ir.config_parameter'].sudo().get_param('pos_whatsapp_chatapi.chat_api_success')
                                    if not is_success:
                                        new_is_success = record.checkChatAPIConnection(chat_api_url, chat_api_token)
                                        if not new_is_success:
                                            #     self.env['ir.config_parameter'].sudo().set_param('pos_whatsapp_chatapi.chat_api_success', new_is_success)
                                            # else:
                                            print("Error while sending a whatsapp message on order#: %s" % (str(record.name),))
                                            continue
                                    # In case the whatsapp is already opened on another device.
                                    record.takeOverRequest(chat_api_url, chat_api_token)
                                    # FIXME: I forced the arabic template to be here.
                                    template = "هنيئاً لكم بداية حكاية جديدة مع عشق، شكراً لكونكم جزءاً من عائلتنا ❤ \n\n ستجدون رصيد الشراء مرفق بالأسفل"
                                    requests.post(str(chat_api_url) + "" + SEND_MESSAGE + "?token=" + str(chat_api_token), data={"phone": phone, "body": template})
                                    data, data_format = record.env.ref('pos_order_print.pos_order_receipt_pdf').render(record.ids)
                                    base64_string = base64.urlsafe_b64encode(data).decode('ascii')
                                    encoded_body = json.dumps( {'phone': phone, 'body': "data:application/pdf;base64," + base64_string, 'filename': str(record.pos_reference) + ".pdf"})
                                    http = urllib3.PoolManager()
                                    http.request('POST', str(chat_api_url) + "" + SEND_FILE + "?token=" + str(chat_api_token), headers={'Content-Type': 'application/json'}, body=encoded_body)
        return res
