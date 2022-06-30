# -*- coding: utf-8 -*-
from odoo import models, api, fields
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_TIME_FORMAT
import datetime
import pytz

def to_tz(datetime, tz_name):
    tz = pytz.timezone(tz_name) if tz_name else pytz.UTC
    return pytz.UTC.localize(datetime.replace(tzinfo=None), is_dst=False).astimezone(tz).replace(tzinfo=None)

class PosOrderReprint(models.Model):
    _inherit = 'pos.order'

    tz_name = fields.Char(string="Timezone", default="Asia/Bahrain", readonly=True)

    @api.model
    def getReceiptData(self, ref):
        result = {}
        order_id = self.search([('pos_reference', '=', ref)], limit=1)
        if order_id:
            products_lines = self.env['pos.order.line'].search([('order_id', '=', order_id.id)])
            result['order_id'] = order_id.id
            result['cashier'] = order_id.user_id.name
            result['change'] = order_id.amount_return
            result['client'] = None # TODO: For future use
            if order_id.partner_id:
                result['client'] = order_id.partner_id.name
                result['client_phone'] = order_id.partner_id.phone
                address = ""
                if order_id.partner_id.country_id:
                    address = order_id.partner_id.country_id.name
                if order_id.partner_id.city:
                    if address != "":
                        address = address + ", " + order_id.partner_id.city
                    else:
                        address = address + order_id.partner_id.city
                if order_id.partner_id.zip:
                    if address != "":
                        address = address + ", B: " + order_id.partner_id.zip
                    else:
                        address = address + order_id.partner_id.zip
                if order_id.partner_id.street:
                    if address != "":
                        address = address + ", R:" + order_id.partner_id.street
                    else:
                        address = address + order_id.partner_id.street
                if order_id.partner_id.street2:
                    if address != "":
                        address = address + ", H:" + order_id.partner_id.street2
                    else:
                        address = address + order_id.partner_id.street2
                result['client_address'] = address
            if order_id.config_id.is_header_or_footer:
                result['footer'] = order_id.config_id.receipt_footer
                result['header'] = order_id.config_id.receipt_header
            else:
                result['footer'] = ''
                result['header'] = ''
            result['invoice_id'] = None # TODO: For future use
            result['name'] = ref
            result['subtotal'] = order_id.amount_total-order_id.amount_tax
            total_discount = 0.000
            orderlines_array = []
            tax_details = []
            checked_taxes = []
            for line in products_lines:
                disc = (line.qty-line.returned_qty)*(1-(line.discount/100.0))*line.price_unit
                total_discount += disc
                orderline_json = {}
                orderline_json["discount"] = line.discount
                orderline_json["price"] = line.price_unit
                orderline_json["price_display"] = line.price_subtotal
                orderline_json["price_with_tax"] = line.price_subtotal_incl
                orderline_json["price_without_tax"] = line.price_subtotal
                orderline_json["product_description"] = False
                orderline_json["product_description_sale"] = False
                orderline_json["product_name"] = line.product_id.name
                orderline_json["product_name_wrapped"] = [line.product_id.name]
                orderline_json["quantity"] = line.qty
                orderline_json["tax"] = line.price_subtotal_incl-line.price_subtotal
                orderline_json["unit_name"] = line.product_id.uom_name
                orderlines_array.append(orderline_json)
                tax_details_json = {}
                for tax in line.tax_ids_after_fiscal_position:
                    if not (tax in checked_taxes):
                        checked_taxes.append(tax)
                        tax_details_json["name"] = tax.name
                        tax_details_json["amount"] = line.price_subtotal_incl-line.price_subtotal
                        tax_details_json["tax"] = { 'name': tax.name,
                                                    'amount': tax.amount,
                                                    'amount_type': tax.amount_type,
                                                    'children_tax_ids': [],
                                                    'id': tax.id,
                                                    'include_base_amount': False,
                                                    'price_include': False}
                        tax_details.append(tax_details_json)
                    else:
                        # Update amount in the current list !
                        for tax_line in tax_details:
                            if tax_line["tax"]["id"]==tax.id:
                                tax_line["amount"] = tax_line["amount"]+(line.price_subtotal_incl-line.price_subtotal)
            # Taxes information:
            result['tax_details'] = tax_details
            # Orderlines information:
            result['orderlines'] = orderlines_array
            #
            result['total_discount'] = total_discount
            result['total_paid'] = order_id.amount_paid
            result['total_tax'] = order_id.amount_tax
            result['total_with_tax'] = order_id.amount_total
            result['total_without_tax'] = order_id.amount_total-order_id.amount_tax
            # Company information:
            company = {}
            company['email'] = order_id.company_id.email
            company['contact_address'] = order_id.company_id.name
            company['street'] = order_id.company_id.street
            company['street2'] = order_id.company_id.street2
            company['zip'] = order_id.company_id.zip
            company['city'] = order_id.company_id.city
            company['logo'] = ''#TODO: Update company logo from pos itself !!
            company['name'] = order_id.company_id.name
            company['phone'] = order_id.company_id.phone
            company['vat'] = False
            company['vat_label'] = order_id.company_id.vat
            company['website'] = order_id.company_id.website
            result['company'] = company
            # Currency Information:
            currency = {}
            currency["id"] = order_id.company_id.currency_id.id
            currency["name"] = order_id.company_id.currency_id.name
            currency["decimals"] = order_id.company_id.currency_id.decimal_places
            currency["position"] = order_id.company_id.currency_id.position
            currency["rate"] = order_id.company_id.currency_id.rate
            currency["rounding"] = order_id.company_id.currency_id.rounding
            currency["symbol"] = order_id.company_id.currency_id.symbol
            result['currency'] = currency
            # date information:
            date_json = {}
            date_order_datetime = datetime.datetime.strptime(datetime.datetime.strftime(order_id.date_order, DEFAULT_SERVER_DATETIME_FORMAT), DEFAULT_SERVER_DATETIME_FORMAT) # Convert to python datetime (Better than odoo datetime library -_-)
            date_json["hour"] = date_order_datetime.hour
            date_json["minute"] = date_order_datetime.minute
            date_json["second"] = date_order_datetime.second
            date_json["isostring"] = date_order_datetime.isoformat()
            date_json["localestring"] = datetime.datetime.strftime(order_id.date_order, DEFAULT_SERVER_DATETIME_FORMAT)
            date_json["day"] = date_order_datetime.weekday()
            date_json["date"] = date_order_datetime.day
            date_json["month"] = date_order_datetime.month
            date_json["year"] = date_order_datetime.year
            date_json["is_reprint"] = True
            date_json["real_date"] = datetime.datetime.strftime(to_tz(order_id.date_order, order_id.tz_name), "%d/%m/%Y")
            date_json["real_time"] = datetime.datetime.strftime(to_tz(order_id.date_order, order_id.tz_name), "%I:%M %p")
            result["date"] = date_json
            # Shop information:
            result["shop"] = {'name':'Stock'} #TODO: Change latter if needed
            # Precision information:
            result["precision"] =   {
                                        'money':2, # TODO: Change latter of needed
                                        'price':2, # TODO: Change latter of needed
                                        'quantity': order_id.company_id.currency_id.decimal_places
                                    }
            # Paymentlines information:
            payments_list = []
            for payment in order_id.statement_ids:
                if not ('return' in payment.name): # Otherwise it is a change for the payment
                    payment_json = {}
                    payment_json['amount'] = payment.amount
                    payment_json['journal'] = payment.journal_id.name
                    payments_list.append(payment_json)
            result['paymentlines'] = payments_list
        return [result]



# receipt: {
# 	'tax_details': [{'amount': 0.067, 'name': 'VAT 5%', tax: {'amount': 5, 'amount_type': 'percent', 'children_tax_ids': [], 'id': 1, 'include_base_amount': False, 'name': 'VAT 5%', 'price_include': False}},....],
# }