from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz

def to_tz(datetime, tz_name):
    tz = pytz.timezone(tz_name) if tz_name else pytz.UTC
    return pytz.UTC.localize(datetime.replace(tzinfo=None), is_dst=False).astimezone(tz).replace(tzinfo=None)

def isPaymentExist(list_var, name):
    for line in list_var:
        if line['name'] == name:
            return True
    return False

def getPayment(list_var, name):
    for line in list_var:
        if line['name'] == name:
            return line['transaction']
    return False

def updatePayment(list_var, name, transaction):
    for line in list_var:
        if line['name'] == name:
            line['transaction'] = transaction
            return list_var
    return False

def addPayment(list_var, name, transaction):
    list_var.append({'name': name, 'transaction': transaction})
    return list_var

class pos_z_receipt(models.TransientModel):
    _name = "report.zreportwizard"

    selected_date = fields.Date('Sessions Date', default=lambda self: fields.Date.today(), help="The Z-Report will include all the sessions happened on this date.")
    tz_name = fields.Char(string="Timezone", default="Asia/Bahrain", readonly=True)
    pos_session_id = fields.Many2one('pos.session', required=True)
    selected_config_id = fields.Many2one('pos.config', related="pos_session_id.config_id", readonly=True)

    @api.multi
    def submit(self):
        all_selected_sessions = self.env['pos.session'].search([('config_id', '=', self.selected_config_id.id), ('start_at', '>=', self.selected_date), ('stop_at', '<=', self.selected_date), ('state', 'in', ['closed', 'closing_control'])], order='start_at')
        zout_report_current_timezone = to_tz(datetime.now(), self.tz_name)
        zout_report = zout_report_current_timezone.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        discount_list = []
        discount_amount = 0.000
        sessions_list = [session_id.name for session_id in all_selected_sessions]
        total_increase = 500  # Default value for the page
        sales_amount = 0
        return_amount = 0
        net_amount = 0
        number_of_sales = 0
        number_of_returns = 0
        number_of_orders = 0
        opening_cash = 0.000
        paid_in_cash = 0.000
        last_ending_cash = 0.000
        net_cash = 0.000
        # TODO: Gather all the payment methods
        bank_payment_methods = []
        paid_in_allcards = 0.000
        cardslist = []
        start_at = ""  # Make it empty to change it on first fetched session
        stop_at = "Not Closed"  # Change it on every session
        branch_name = "ERROR"
        cashier = "ERROR"
        total_cash = 0.000
        if len(all_selected_sessions) == 0:
            raise Warning(_("There is no sessions on the selected date !"))
        for session in all_selected_sessions:
            branch_name = session.config_id.branch_name
            cashier = session.user_id.display_name
            if start_at == "":
                start_at = to_tz(session.start_at, self.tz_name).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            if session.stop_at:
                stop_at = to_tz(session.stop_at, self.tz_name).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            for order in session.order_ids:
                # Collect all the cash from all orders assigned to this session
                order_cash = 0.000
                if order.state in ['paid', 'done', 'posted']:
                    for payment in order.statement_ids:
                        if payment.journal_id.type == 'cash':
                            total_cash += payment.amount
                            order_cash += payment.amount
                        else:
                            if payment.amount > 0:
                                cardslist.append(
                                    {
                                        'name': payment.journal_id.name,
                                        'amount': payment.amount
                                    }
                                )
                if order_cash > 0:
                    cardslist.append(
                        {
                            'name': "Cash",
                            'amount': order_cash
                        }
                    )
                number_of_orders += 1
                if order.amount_paid > 0:
                    sales_amount = sales_amount + order.amount_paid
                    number_of_sales = number_of_sales + 1
                else:
                    return_amount = return_amount + order.amount_paid
                    number_of_returns = number_of_returns + 1
                for order_line in order.lines.filtered(lambda line: line.discount > 0):
                    customer = "N/A"
                    if order.partner_id:
                        customer = order.partner_id.name
                    discount_list.append({'product': order_line.product_id.name, 'customer': customer, 'qty': order_line.qty, 'amount': order_line.discount, 'type': order.discount_type})
                    discount_amount_temp = (order_line.price_unit - (order_line.price_subtotal / order_line.qty))
                    if order_line.qty < 0:  # A return
                        discount_amount += -1 * discount_amount_temp
                    else:
                        discount_amount += discount_amount_temp
            net_amount = sales_amount + return_amount
            # Payment methods: statement_ids
            for statement_id in session.statement_ids:
                if statement_id.journal_id.type == "cash":
                    if opening_cash == 0:  # Take the first opening cash
                        opening_cash = statement_id.balance_start
                    paid_in_cash = paid_in_cash + statement_id.total_entry_encoding
                    last_ending_cash = statement_id.balance_end_real
                else:  # Sure it is bank now
                    paid_in_allcards = paid_in_allcards + statement_id.total_entry_encoding
                    if isPaymentExist(bank_payment_methods, statement_id.journal_id.name):
                        transaction = getPayment(bank_payment_methods, statement_id.journal_id.name)
                        updatePayment(bank_payment_methods, statement_id.journal_id.name, statement_id.total_entry_encoding+transaction)
                    else:
                        addPayment(bank_payment_methods, statement_id.journal_id.name, statement_id.total_entry_encoding)
            net_cash = session.cash_register_balance_end_real  # Only last closing balance
            # total_increase += len(cardslist) * 8.0  # Spacing by 8mm
            # total_increase += len(sessions_list) * 8.0  # Spacing by 8mm
            # total_increase += len(bank_payment_methods) * 16.0  # Spacing (For Two Lines)
        short_excess_cash = last_ending_cash - (paid_in_cash + opening_cash)
        paper_format = self.env['report.paperformat'].search([('name', '=', 'POS Z-Report')])
        paper_format.page_height = total_increase  # 500 is the normal height without changing
        datas = {
            'zout_report': zout_report,
            'start_at': start_at,
            'stop_at': stop_at,
            'branch_name': branch_name,
            'cashier': cashier,
            'sales_amount': sales_amount,
            'return_amount': return_amount,
            'net_amount': net_amount,
            'number_of_sales': number_of_sales,
            'number_of_returns': number_of_returns,
            'number_of_orders': number_of_orders,
            'opening_cash': opening_cash,
            'paid_in_cash': paid_in_cash,
            'short_excess_cash': short_excess_cash,
            'net_cash': net_cash,
            'paid_in_allcards': paid_in_allcards,
            'short_excess_allcards': paid_in_allcards * -1,
            'net_allcards': paid_in_allcards,
            'cardslist': cardslist,
            'sessions_list': sessions_list,
            'discount_list': discount_list,
            'discount_amount': discount_amount,
            'bank_payment_methods': bank_payment_methods,
            'total_cash': total_cash,
        }
        return self.env.ref('pos_session_report.zreport_pdf_session_receipt').report_action(self, data=datas)

class pos_z_receipt_template(models.AbstractModel):
    _name = 'report.pos_session_report.pos_z_receipt_template'

    @api.multi
    def _get_report_values(self, docids, data=None):
        docargs = {
                  'doc_ids': self.ids,
                  'data':data
                   }
        return docargs