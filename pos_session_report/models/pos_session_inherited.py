# -*- coding: utf-8 -*-
# This module is using Asia/Bahrain as a fixed timezone

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz

def to_tz(datetime, tz_name):
    tz = pytz.timezone(tz_name) if tz_name else pytz.UTC
    return pytz.UTC.localize(datetime.replace(tzinfo=None), is_dst=False).astimezone(tz).replace(tzinfo=None)

class pos_session_report(models.Model):
    _inherit = 'pos.session'

    tz_name = fields.Char(string="Timezone", default="Asia/Bahrain", readonly=True, store=True)

    @api.multi
    def action_pos_session_report_as_receipt(self):
        xout_report_current_timezone = to_tz(datetime.now(), self.tz_name)
        xout_report = xout_report_current_timezone.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        branch_name = self.config_id.branch_name
        store_number = self.config_id.store_number
        workstation_number = self.config_id.workstation_number
        cashier = self.user_id.display_name
        start_at = to_tz(self.start_at, self.tz_name).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        stop_at = "Not Closed"
        if self.stop_at:
            stop_at = to_tz(self.stop_at, self.tz_name).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        sales_amount = 0
        return_amount = 0
        net_amount = 0
        number_of_sales = 0
        number_of_returns = 0
        for order in self.order_ids:
            sales_amount = sales_amount+order.amount_paid
            return_amount = return_amount+order.amount_return
            net_amount = net_amount+order.amount_total
        opening_cash = 0.000
        paid_in_cash = 0.000
        paid_out_cash = 0.000 #TODO: What is this ???
        short_excess_cash = 0.000
        net_cash = 0.000
        paid_in_allcards = 0.000
        paid_out_allcards = 0.000 #TODO: What is this ???
        paid_in_VISA = 0.000
        paid_out_VISA = 0.000 #TODO: What is this ???
        paid_in_MASTER = 0.000
        paid_out_MASTER = 0.000 #TODO: What is this ???
        paid_in_MAESTRO = 0.000
        paid_out_MAESTRO = 0.000 #TODO: What is this ???
        paid_in_AMEX = 0.000
        paid_out_AMEX = 0.000 #TODO: What is this ???
        paid_in_JPC = 0.000
        paid_out_JPC = 0.000 #TODO: What is this ???
        paid_in_DEBIT = 0.000
        paid_out_DEBIT = 0.000 #TODO: What is this ???
        paid_in_RPRO_CCN = 0.000
        paid_out_RPRO_CCN = 0.000 #TODO: What is this ???
        paid_in_TAP_PAY = 0.000
        paid_out_TAP_PAY = 0.000 #TODO: What is this ???
        paid_in_CREDIMAX_QR = 0.000
        paid_out_CREDIMAX_QR = 0.000 #TODO: What is this ???
        paid_in_BWALLET = 0.000
        paid_out_BWALLET = 0.000 #TODO: What is this ???
        paid_in_VIVA_CASH = 0.000
        paid_out_VIVA_CASH = 0.000 #TODO: What is this ???
        cardslist = []
        VISA_count = 0
        MASTER_count = 0
        MAESTRO_count = 0
        AMEX_count = 0
        JPC_count = 0
        DEBIT_count = 0
        RPRO_CCN_count = 0
        TAP_PAY_count = 0
        CREDIMAX_QR_count = 0
        BWALLET_count = 0
        VIVA_CASH_count = 0
        #Payment methods: statement_ids
        for statement_id in self.statement_ids:
            if statement_id.journal_id.type=="cash":
                opening_cash = opening_cash+statement_id.balance_start
                paid_in_cash = paid_in_cash+statement_id.total_entry_encoding
                paid_out_cash = 0.000  # TODO: What is this ???
                short_excess_cash = short_excess_cash+statement_id.balance_end_real * -1
                net_cash = net_cash+statement_id.balance_end_real
                for transaction in statement_id.line_ids:
                    if transaction.amount < 0:
                        number_of_returns = number_of_returns + 1
                    else:
                        number_of_sales = number_of_sales + 1
            else:
                paid_in_allcards = paid_in_allcards+statement_id.total_entry_encoding
                paid_out_allcards = 0.000  # TODO: What is this ???
                if (("VISA" in statement_id.journal_id.name) or ("visa" in statement_id.journal_id.name)):
                    if (statement_id.total_entry_encoding > 0):
                        paid_in_VISA = paid_in_VISA+statement_id.total_entry_encoding
                        paid_out_VISA = 0.000  # TODO: What is this ???
                        #  for all transactions
                        for transaction in statement_id.line_ids:
                            if transaction.amount<0:
                                number_of_returns=number_of_returns+1
                            else:
                                number_of_sales = number_of_sales + 1
                            cardslist.append(
                                {
                                    'name': "VISA",
                                    'amount': transaction.amount
                                }
                            )
                            VISA_count = VISA_count + 1
                elif (("MAESTRO" in statement_id.journal_id.name) or ("mastero" in statement_id.journal_id.name)):
                    if (statement_id.total_entry_encoding>0):
                        paid_in_MAESTRO = paid_in_MAESTRO+statement_id.total_entry_encoding
                        paid_out_MAESTRO = 0.000  # TODO: What is this ???
                        #  for all transactions
                        for transaction in statement_id.line_ids:
                            if transaction.amount<0:
                                number_of_returns=number_of_returns+1
                            else:
                                number_of_sales = number_of_sales + 1
                            cardslist.append(
                                {
                                    'name': "MAESTRO",
                                    'amount': transaction.amount
                                }
                            )
                            MAESTRO_count = MAESTRO_count + 1
                elif (("MASTER" in statement_id.journal_id.name) or ("master" in statement_id.journal_id.name)):
                    if (statement_id.total_entry_encoding>0):
                        paid_in_MASTER = paid_in_MASTER+statement_id.total_entry_encoding
                        paid_out_MASTER = 0.000  # TODO: What is this ???
                        #  for all transactions
                        for transaction in statement_id.line_ids:
                            if transaction.amount<0:
                                number_of_returns=number_of_returns+1
                            else:
                                number_of_sales = number_of_sales + 1
                            cardslist.append(
                                {
                                    'name': "MASTER",
                                    'amount': transaction.amount
                                }
                            )
                            MASTER_count = MASTER_count + 1
                elif (("AMEX" in statement_id.journal_id.name) or ("amex" in statement_id.journal_id.name)):
                    if (statement_id.total_entry_encoding>0):
                        paid_in_AMEX = paid_in_AMEX+statement_id.total_entry_encoding
                        paid_out_AMEX = 0.000  # TODO: What is this ???
                        #  for all transactions
                        for transaction in statement_id.line_ids:
                            if transaction.amount<0:
                                number_of_returns=number_of_returns+1
                            else:
                                number_of_sales = number_of_sales + 1
                            cardslist.append(
                                {
                                    'name': "AMEX",
                                    'amount': transaction.amount
                                }
                            )
                            AMEX_count = AMEX_count + 1
                elif (("JPC" in statement_id.journal_id.name) or ("jpc" in statement_id.journal_id.name)):
                    if (statement_id.total_entry_encoding>0):
                        paid_in_JPC = paid_in_JPC+statement_id.total_entry_encoding
                        paid_out_JPC = 0.000  # TODO: What is this ???
                        #  for all transactions
                        for transaction in statement_id.line_ids:
                            if transaction.amount<0:
                                number_of_returns=number_of_returns+1
                            else:
                                number_of_sales = number_of_sales + 1
                            cardslist.append(
                                {
                                    'name': "JPC",
                                    'amount': transaction.amount
                                }
                            )
                            JPC_count = JPC_count + 1
                elif (("DEBIT" in statement_id.journal_id.name) or ("debit" in statement_id.journal_id.name)):
                    if (statement_id.total_entry_encoding>0):
                        paid_in_DEBIT = paid_in_DEBIT+statement_id.total_entry_encoding
                        paid_out_DEBIT = 0.000  # TODO: What is this ???
                        #  for all transactions
                        for transaction in statement_id.line_ids:
                            if transaction.amount<0:
                                number_of_returns=number_of_returns+1
                            else:
                                number_of_sales = number_of_sales + 1
                            cardslist.append(
                                {
                                    'name': "DEBIT",
                                    'amount': transaction.amount
                                }
                            )
                            DEBIT_count = DEBIT_count + 1
                elif (("RPRO CCN" in statement_id.journal_id.name) or ("rpro ccn" in statement_id.journal_id.name)):
                    if (statement_id.total_entry_encoding>0):
                        paid_in_RPRO_CCN = paid_in_RPRO_CCN+statement_id.total_entry_encoding
                        paid_out_RPRO_CCN = 0.000  # TODO: What is this ???
                        #  for all transactions
                        for transaction in statement_id.line_ids:
                            if transaction.amount<0:
                                number_of_returns=number_of_returns+1
                            else:
                                number_of_sales = number_of_sales + 1
                            cardslist.append(
                                {
                                    'name': "RPRO CCN",
                                    'amount': transaction.amount
                                }
                            )
                            RPRO_CCN_count = RPRO_CCN_count + 1
                elif (("TAP PAY" in statement_id.journal_id.name) or ("tap pay" in statement_id.journal_id.name)):
                    if (statement_id.total_entry_encoding>0):
                        paid_in_TAP_PAY = paid_in_TAP_PAY+statement_id.total_entry_encoding
                        paid_out_TAP_PAY = 0.000  # TODO: What is this ???
                        #  for all transactions
                        for transaction in statement_id.line_ids:
                            if transaction.amount<0:
                                number_of_returns=number_of_returns+1
                            else:
                                number_of_sales = number_of_sales + 1
                            cardslist.append(
                                {
                                    'name': "TAP PAY",
                                    'amount': transaction.amount
                                }
                            )
                            TAP_PAY_count = TAP_PAY_count + 1
                elif (("CREDIMAX QR" in statement_id.journal_id.name) or ("credimax qr" in statement_id.journal_id.name)):
                    if (statement_id.total_entry_encoding>0):
                        paid_in_CREDIMAX_QR = paid_in_CREDIMAX_QR+statement_id.total_entry_encoding
                        paid_out_CREDIMAX_QR = 0.000  # TODO: What is this ???
                        #  for all transactions
                        for transaction in statement_id.line_ids:
                            if transaction.amount<0:
                                number_of_returns=number_of_returns+1
                            else:
                                number_of_sales = number_of_sales + 1
                            cardslist.append(
                                {
                                    'name': "CREDIMAX QR",
                                    'amount': transaction.amount
                                }
                            )
                            CREDIMAX_QR_count = CREDIMAX_QR_count + 1
                elif (("BWALLET" in statement_id.journal_id.name) or ("bwallet" in statement_id.journal_id.name)):
                    if (statement_id.total_entry_encoding>0):
                        paid_in_BWALLET = paid_in_BWALLET+statement_id.total_entry_encoding
                        paid_out_BWALLET = 0.000  # TODO: What is this ???
                        #  for all transactions
                        for transaction in statement_id.line_ids:
                            if transaction.amount<0:
                                number_of_returns=number_of_returns+1
                            else:
                                number_of_sales = number_of_sales + 1
                            cardslist.append(
                                {
                                    'name': "BWALLET",
                                    'amount': transaction.amount
                                }
                            )
                            BWALLET_count = BWALLET_count + 1
                elif (("VIVA CASH" in statement_id.journal_id.name) or ("viva cash" in statement_id.journal_id.name)):
                    if (statement_id.total_entry_encoding>0):
                        paid_in_VIVA_CASH = paid_in_VIVA_CASH+statement_id.total_entry_encoding
                        paid_out_VIVA_CASH = 0.000  # TODO: What is this ???
                        #  for all transactions
                        for transaction in statement_id.line_ids:
                            if transaction.amount<0:
                                number_of_returns=number_of_returns+1
                            else:
                                number_of_sales = number_of_sales + 1
                            cardslist.append(
                                {
                                    'name': "VIVA CASH",
                                    'amount': transaction.amount
                                }
                            )
                            VIVA_CASH_count = VIVA_CASH_count + 1
        paper_format = self.env['report.paperformat'].search([('name', '=', 'POS Session Report')])
        total_increase = len(cardslist)*8.0 # Spacing by 5mm for each card purchase
        if (MAESTRO_count!=0):
            total_increase+=80
        elif (AMEX_count!=0):
            total_increase += 80
        elif (JPC_count != 0):
            total_increase += 80
        elif (DEBIT_count != 0):
            total_increase += 80
        elif (RPRO_CCN_count != 0):
            total_increase += 80
        elif (TAP_PAY_count != 0):
            total_increase += 80
        elif (CREDIMAX_QR_count != 0):
            total_increase += 80
        elif (BWALLET_count != 0):
            total_increase += 80
        elif (VIVA_CASH_count != 0):
            total_increase += 80
        paper_format.page_width = total_increase+500 # 500 is the normal height without changing
        datas = {
            'xout_report': xout_report,
            'start_at': start_at,
            'stop_at': stop_at,
            'branch_name': branch_name,
            'store_number': store_number,
            'workstation_number': workstation_number,
            'cashier': cashier,
            'session_id': self.name,
            'sales_amount': sales_amount,
            'return_amount': return_amount*-1,
            'net_amount': net_amount,
            'number_of_sales': number_of_sales,
            'number_of_returns': number_of_returns,
            'opening_cash': opening_cash,
            'paid_in_cash': paid_in_cash,
            'paid_out_cash': paid_out_cash,
            'short_excess_cash': short_excess_cash,
            'net_cash': net_cash,
            'paid_in_allcards': paid_in_allcards,
            'paid_out_allcards': paid_out_allcards,
            'short_excess_allcards': paid_in_allcards*-1,
            'net_allcards': paid_in_allcards,
            'paid_in_VISA': paid_in_VISA,
            'paid_out_VISA': paid_out_VISA,
            'short_excess_VISA': paid_in_VISA*-1,
            'net_VISA': paid_in_VISA,
            'paid_in_MASTER': paid_in_MASTER,
            'paid_out_MASTER': paid_out_MASTER,
            'short_excess_MASTER': paid_in_MASTER*-1,
            'net_MASTER': paid_in_MASTER,
            'paid_in_MAESTRO': paid_in_MAESTRO,
            'paid_out_MAESTRO': paid_out_MAESTRO,
            'short_excess_MAESTRO': paid_in_MAESTRO * -1,
            'net_MAESTRO': paid_in_MAESTRO,
            'paid_in_AMEX': paid_in_AMEX,
            'paid_out_AMEX': paid_out_AMEX,
            'short_excess_AMEX': paid_in_AMEX * -1,
            'net_AMEX': paid_in_AMEX,
            'paid_in_JPC': paid_in_JPC,
            'paid_out_JPC': paid_out_JPC,
            'short_excess_JPC': paid_in_JPC * -1,
            'net_JPC': paid_in_JPC,
            'paid_in_DEBIT': paid_in_DEBIT,
            'paid_out_DEBIT': paid_out_DEBIT,
            'short_excess_DEBIT': paid_in_DEBIT * -1,
            'net_DEBIT': paid_in_DEBIT,
            'paid_in_RPRO_CCN': paid_in_RPRO_CCN,
            'paid_out_RPRO_CCN': paid_out_RPRO_CCN,
            'short_excess_RPRO_CCN': paid_in_RPRO_CCN * -1,
            'net_RPRO_CCN': paid_in_RPRO_CCN,
            'paid_in_TAP_PAY': paid_in_TAP_PAY,
            'paid_out_TAP_PAY': paid_out_TAP_PAY,
            'short_excess_TAP_PAY': paid_in_TAP_PAY * -1,
            'net_TAP_PAY': paid_in_TAP_PAY,
            'paid_in_CREDIMAX_QR': paid_in_CREDIMAX_QR,
            'paid_out_CREDIMAX_QR': paid_out_CREDIMAX_QR,
            'short_excess_CREDIMAX_QR': paid_in_CREDIMAX_QR * -1,
            'net_CREDIMAX_QR': paid_in_CREDIMAX_QR,
            'paid_in_BWALLET': paid_in_BWALLET,
            'paid_out_BWALLET': paid_out_BWALLET,
            'short_excess_BWALLET': paid_in_BWALLET * -1,
            'net_BWALLET': paid_in_BWALLET,
            'paid_in_VIVA_CASH': paid_in_VIVA_CASH,
            'paid_out_VIVA_CASH': paid_out_VIVA_CASH,
            'short_excess_VIVA_CASH': paid_in_VIVA_CASH * -1,
            'net_VIVA_CASH': paid_in_VIVA_CASH,
            'cardslist': cardslist,
            'MASTER_count': MASTER_count,
            'VISA_count': VISA_count,
            'MAESTRO_count': MAESTRO_count,
            'AMEX_count': AMEX_count,
            'JPC_count': JPC_count,
            'DEBIT_count': DEBIT_count,
            'RPRO_CCN_count': RPRO_CCN_count,
            'TAP_PAY_count': TAP_PAY_count,
            'CREDIMAX_QR_count': CREDIMAX_QR_count,
            'BWALLET_count': BWALLET_count,
            'VIVA_CASH_count': VIVA_CASH_count,
        }
        return self.env.ref('pos_session_report.report_pdf_session_receipt').report_action(self, data=datas)