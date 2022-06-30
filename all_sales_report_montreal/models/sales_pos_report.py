# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_TIME_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
import datetime
import pytz
import json

def to_tz(datetime, tz_name):
    tz = pytz.timezone(tz_name) if tz_name else pytz.UTC
    return pytz.UTC.localize(datetime.replace(tzinfo=None), is_dst=False).astimezone(tz).replace(tzinfo=None)

def isQuotationAdded(list,quotation_number):
    if str(quotation_number) in list:
        return True
    return False

def addQuotation(list,quotation_number,partner,payment_amount,amount_due,payment_percentage):
    if isQuotationAdded(list, quotation_number):
        return False
    data = {
        'quotation_number': quotation_number,
        'partner': partner,
        'amount_due':float(amount_due),
        'payment_amount':float(payment_amount),
        'payment_percentage':float(payment_percentage)
        }
    list[str(quotation_number)] = data
    return True

def isPaymentAdded(list,payment_id):
    if str(payment_id) in list:
        return True
    return False

def addPayment(list,payment_id,payment_name,payment_amount):
    if isPaymentAdded(list, payment_id):
        return False
    data = {
        'payment_name': payment_name,
        'payment_amount':float(payment_amount),
        }
    list[str(payment_id)] = data
    return True

def updatePaymentData(list,payment_id,data_type,new_value):
    if isPaymentAdded(list,payment_id):
        data = list[str(payment_id)]
        data[data_type] = new_value
        list[str(payment_id)] = data
        return True
    return False

def getPaymentData(list,payment_id,data_type):
    if isPaymentAdded(list,payment_id):
        data = list[str(payment_id)]
        return data[data_type]
    return False

def isProductAdded(list,id,unit_price,discount):
    if str(id)+"_"+str(unit_price)+"_"+str(discount) in list:
        return True
    return False

def addProduct(list,product_name,id,unit_price,discount,uom_name):
    if isProductAdded(list, id, unit_price, discount):
        return False
    data = {
        'name': product_name,
        'quantity':0.000,
        'uom_name':uom_name,
        'unit_price':float(unit_price),
        'taxable_amount':0.000,
        'VAT':0.000,
        'amount_incl_VAT': 0.000,
        'discount': float(discount)
        }
    list[str(id)+"_"+str(unit_price)+"_"+str(discount)] = data
    return True

def updateProductData(list,id,unit_price,discount,data_type,new_value):
    if isProductAdded(list,id,unit_price,discount):
        data = list[str(id)+"_"+str(unit_price)+"_"+str(discount)]
        data[data_type] = new_value
        list[str(id)+"_"+str(unit_price)+"_"+str(discount)] = data
        return True
    return False

def getProductData(list,id,unit_price,discount,data_type):
    if isProductAdded(list,id,unit_price,discount):
        data = list[str(id)+"_"+str(unit_price)+"_"+str(discount)]
        return data[data_type]
    return False

class all_sales_report(models.TransientModel):
    _name = 'report.sales_pos_report_wizard'

    start_date = fields.Datetime('Start Date', required=True)
    end_date = fields.Datetime('Start Date', required=True)

    tz_name = fields.Char(string="Timezone", default="Asia/Bahrain", readonly=True)

    @api.multi
    def action_submit(self):
        all_pos_orders = self.env['pos.order'].search([('date_order', '>=', self.start_date), ('date_order', '<=', self.end_date)])
        #
        VAT_array = []  # 0 is total of VAT, 1 is total untaxed amount
        VAT_array.append(0.000)
        VAT_array.append(0.000)
        # VAT Calculation for "VAT Received" Account Only ! - Start
        all_vat = self.env['account.move.line'].search([('date', '>=', self.start_date), ('date', '<=', self.end_date)])
        for move_line in all_vat:
            account_name = move_line.account_id.name
            if "VAT Received".lower() in account_name.lower():
                vat_amount = move_line.credit
                VAT_array[0] = VAT_array[0] + float(vat_amount)
        VAT_array[1] = VAT_array[0]*20  # Dummy calculation to show the untaxed_amount
        # VAT Calculation for "111200 VAT Received" Account Only ! - End
        # Sales Variables - Start (Only for Whole Sale)
        all_vendor_bills = self.env['account.invoice'].search([('date_invoice', '>=', self.start_date), ('date_invoice', '<=', self.end_date), ('type', '=', 'out_invoice'), ('state', 'not in', ['draft','cancel'])])
        payments_POs = []  # This will be used whenever there is a quotation not in the search all_sale_orders variable (BILLs)
        #
        checked_payments = []
        VAT_array = []  # 0 is total of VAT, 1 is total untaxed amount
        VAT_array.append(0.000)
        VAT_array.append(0.000)
        # Purchase Variables - Start
        sales_quotations = {}
        sales_products = {}
        sales_payments = {}
        for bill in all_vendor_bills:
            for payment_id in bill.payment_ids:
                if payment_id.id not in checked_payments:
                    if isPaymentAdded(sales_payments, payment_id.journal_id.name):
                        payment_amount = getPaymentData(sales_payments, payment_id.journal_id.name, "payment_amount")
                        updatePaymentData(sales_payments, payment_id.journal_id.name, "payment_amount", payment_amount + float(payment_id.amount))
                    else:
                        addPayment(sales_payments, payment_id.journal_id.name, payment_id.journal_id.name, float(payment_id.amount))
                    checked_payments.append(payment_id.id)
            # Remove the matched quotations:
            if bill.id in payments_POs:
                payments_POs.remove(bill.id)  # We do not want to show a duplicate !!
            invoiced_amount = bill.amount_total-bill.residual
            if bill.amount_total > 0:
                invoiced_amount_percentage = round(100 * invoiced_amount / bill.amount_total, 3)
            else:
                invoiced_amount_percentage = 0.0
            addQuotation(sales_quotations, bill.number, bill.partner_id.name if bill.partner_id else "", bill.amount_total, bill.residual, invoiced_amount_percentage)
            # if order.invoice_count > 0:
            #     related_invoices = order.invoice_ids
            #     for invoice_line in related_invoices:
            #         # payments_id = invoice_line.payment_ids -> This one have a problem !!!!
            #         payments = json.loads(invoice_line.payments_widget)
            #         if payments:
            #             for payment in payments["content"]:
            #                 if isPaymentAdded(sales_payments, payment["journal_name"]):
            #                     payment_amount = getPaymentData(sales_payments, payment["journal_name"], "payment_amount")
            #                     updatePaymentData(sales_payments, payment["journal_name"], "payment_amount", payment_amount + float(payment["amount"]))
            #                 else:
            #                     addPayment(sales_payments, payment["journal_name"], payment["journal_name"], float(payment["amount"]))
            for line in bill.invoice_line_ids:
                price_unit = float(line.price_unit)
                ordered_qty = line.quantity
                if line.product_id:
                    product = line.product_id
                else:
                    product = line  # Just to get around the product
                discount = 0
                if isProductAdded(sales_products,product.id,price_unit,discount):
                    VAT_array[0] = VAT_array[0]+float(line.price_tax)
                    if float(line.price_tax) > 0:
                        VAT_array[1] = VAT_array[1]+float(line.price_subtotal)
                    current_qty = getProductData(sales_products,product.id,price_unit,discount,"quantity")
                    taxable_amount = getProductData(sales_products,product.id,price_unit,discount,"taxable_amount")
                    VAT = getProductData(sales_products,product.id,price_unit,discount,"VAT")
                    amount_incl_VAT = getProductData(sales_products,product.id,price_unit,discount,"amount_incl_VAT")
                    updateProductData(sales_products, product.id, price_unit, discount, "quantity", ordered_qty+current_qty)
                    updateProductData(sales_products, product.id, price_unit, discount, "taxable_amount", taxable_amount+float(line.price_subtotal))
                    updateProductData(sales_products, product.id, price_unit, discount, "VAT", VAT+float(line.price_tax))
                    updateProductData(sales_products, product.id, price_unit, discount, "amount_incl_VAT", amount_incl_VAT+float(line.price_total))
                else:
                    VAT_array[0] = VAT_array[0] + float(line.price_tax)
                    if float(line.price_tax) > 0:
                        VAT_array[1] = VAT_array[1] + float(line.price_subtotal)
                    addProduct(sales_products, product.name, product.id, price_unit, discount, "")
                    updateProductData(sales_products, product.id, price_unit, discount, "quantity", ordered_qty)
                    updateProductData(sales_products, product.id, price_unit, discount, "taxable_amount", float(line.price_subtotal))
                    updateProductData(sales_products, product.id, price_unit, discount, "VAT", float(line.price_tax))
                    updateProductData(sales_products, product.id, price_unit, discount, "amount_incl_VAT", float(line.price_total))
        # Sales Variables - End
        # POS Variables - Start (For both: Retail and WholeSale)
        all_pos_products = {}
        all_pos_payments = {}
        for pos_order in all_pos_orders:
            for pos_payment in pos_order.statement_ids:
                journal = pos_payment.journal_id
                if isPaymentAdded(all_pos_payments, journal.id):
                    payment_amount = getPaymentData(all_pos_payments, journal.id, "payment_amount")
                    updatePaymentData(all_pos_payments, journal.id, "payment_amount", payment_amount+float(pos_payment.amount))
                else:
                    addPayment(all_pos_payments, journal.id, journal.name, float(pos_payment.amount))
            for pos_line in pos_order.lines:
                price_unit = float(pos_line.price_unit)
                ordered_qty = pos_line.qty
                product = pos_line.product_id
                discount = pos_line.discount
                if isProductAdded(all_pos_products, product.id, price_unit, discount):
                    # VAT_array[0] = VAT_array[0] + (float(pos_line.price_subtotal_incl) - float(pos_line.price_subtotal))
                    # if (float(pos_line.price_subtotal_incl) - float(pos_line.price_subtotal)) > 0:
                    #     VAT_array[1] = VAT_array[1] + float(pos_line.price_subtotal)
                    current_qty = getProductData(all_pos_products, product.id, price_unit, discount, "quantity")
                    taxable_amount = getProductData(all_pos_products, product.id, price_unit, discount, "taxable_amount")
                    VAT = getProductData(all_pos_products, product.id, price_unit, discount, "VAT")
                    amount_incl_VAT = getProductData(all_pos_products, product.id, price_unit, discount, "amount_incl_VAT")
                    updateProductData(all_pos_products, product.id, price_unit, discount, "quantity", ordered_qty + current_qty)
                    updateProductData(all_pos_products, product.id, price_unit, discount, "taxable_amount", taxable_amount + float(pos_line.price_subtotal))
                    updateProductData(all_pos_products, product.id, price_unit, discount, "VAT", VAT + (float(pos_line.price_subtotal_incl) - float(pos_line.price_subtotal)))
                    updateProductData(all_pos_products, product.id, price_unit, discount, "amount_incl_VAT", amount_incl_VAT + float(pos_line.price_subtotal_incl))
                else:
                    # VAT_array[0] = VAT_array[0] + (float(pos_line.price_subtotal_incl) - float(pos_line.price_subtotal))
                    # if (float(pos_line.price_subtotal_incl) - float(pos_line.price_subtotal)) > 0:
                    #     VAT_array[1] = VAT_array[1] + float(pos_line.price_subtotal)
                    addProduct(all_pos_products, product.name, product.id, price_unit, discount, product.uom_name)
                    updateProductData(all_pos_products, product.id, price_unit, discount, "quantity", ordered_qty)
                    updateProductData(all_pos_products, product.id, price_unit, discount, "taxable_amount", float(pos_line.price_subtotal))
                    updateProductData(all_pos_products, product.id, price_unit, discount, "VAT", float(pos_line.price_subtotal_incl) - float(pos_line.price_subtotal))
                    updateProductData(all_pos_products, product.id, price_unit, discount, "amount_incl_VAT", float(pos_line.price_subtotal_incl))
        # POS Variables - End
        datas = {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'sales_products': sales_products,
            'sales_payments': sales_payments,
            'all_pos_products': all_pos_products,
            'all_pos_payments': all_pos_payments,
            'sales_quotations': sales_quotations,
            'VAT': VAT_array
        }
        return self.env.ref('all_sales_report_montreal.all_sales_report_pdf').report_action(self, data=datas)

class all_sales_report_template(models.AbstractModel):
    _name = 'report.all_sales_report_montreal.sales_pos_report'

    @api.multi
    def _get_report_values(self, docids, data=None):
        # print("data: " + str(data))
        docargs = {
            'doc_ids': self.ids,
            'data': data,
        }
        return docargs