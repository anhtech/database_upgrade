# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_TIME_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
import datetime
import pytz
import xlwt
from io import StringIO
import base64



def isProductAdded(list,id):
    if str(id) in list:
        return True
    return False

def addProduct(list,product_name,pos_categ,id,qty_available):
    if isProductAdded(list, id):
        return False
    data = {
        'name': product_name,
        'pos_categ': pos_categ,
        'units_sold':0.000,
        'sales':0.000,
        'costs':0.000,
        'gross_profit':0.000,
        'percentage':0.0,
        'qty_on_hand': float(qty_available)
        }
    list[str(id)] = data
    return True

def updateProductData(list,id,data_type,new_value):
    if isProductAdded(list,id):
        data = list[str(id)]
        data[data_type] = new_value
        list[str(id)] = data
        return True
    return False

def getProductData(list,id,data_type):
    if isProductAdded(list,id):
        data = list[str(id)]
        return data[data_type]
    return False

def isCategoryAdded(list,category_name):
    if str(category_name) in list:
        return True
    return False

def addCategory(list,category_name,qty_available):
    if isCategoryAdded(list, category_name):
        return False
    data = {
        'name': category_name,
        'units_sold':0.000,
        'sales':0.000,
        'costs':0.000,
        'gross_profit':0.000,
        'percentage':0.0,
        'qty_on_hand': float(qty_available)
        }
    list[str(category_name)] = data
    return True

def updateCategoryData(list,category_name,data_type,new_value):
    if isCategoryAdded(list,category_name):
        data = list[str(category_name)]
        data[data_type] = new_value
        list[str(category_name)] = data
        return True
    return False

def getCategoryData(list,category_name,data_type):
    if isCategoryAdded(list,category_name):
        data = list[str(category_name)]
        return data[data_type]
    return False

def to_tz(datetime, tz_name):
    tz = pytz.timezone(tz_name) if tz_name else pytz.UTC
    return pytz.UTC.localize(datetime.replace(tzinfo=None), is_dst=False).astimezone(tz).replace(tzinfo=None)

class StockReportWizard(models.TransientModel):
    _name = "report.stock.wizard"

    start_date = fields.Date('Start Date', required=True, defualt=datetime.datetime.now().date().replace(day=1))
    end_date = fields.Date('End Date', required=True, default=datetime.datetime.now().date())
    pricelist_ids = fields.Many2many('product.pricelist', string="Pricelists")

    include_pos = fields.Boolean(string="Include POS Orders?", default=True)
    include_sale = fields.Boolean(string="Include Sale Orders?", default=True)

    include_all_products = fields.Boolean(string="Include All Products?", default=True)
    product_ids = fields.Many2many('product.product', string="Products")

    tz_name = fields.Char(string="Timezone",default="Asia/Bahrain",readonly=True)

    @api.onchange('include_all_products')
    def _onIncludeAllProductsChange(self):
        if self.include_all_products:
            self.product_ids = False

    # def getUnitCostFromStockValuationLayer(self, is_so=False, sale_id=False, is_pos_order=False, pos_order_id=False, product_id=False):
    #     if is_so and is_pos_order:
    #         raise UserError(_("Wrong use of getCostFromStockValuationLayer function!"))
    #     if not product_id:
    #         UserError(_("You must provide a product!"))
    #     if is_so:
    #         if not sale_id:
    #             UserError(_("You must provide a sale order!"))
    #         stock_valuation_layer_id = self.env['stock.valuation.layer'].search([('product_id', '=', product_id.id), ('stock_move_id.origin', '=', sale_id.name)], limit=1)
    #         if stock_valuation_layer_id:
    #             return stock_valuation_layer_id.unit_cost
    #         return False
    #     elif is_pos_order:
    #         if not pos_order_id:
    #             UserError(_("You must provide a pos order!"))
    #         stock_valuation_layer_id = self.env['stock.valuation.layer'].search([('product_id', '=', product_id.id), ('stock_move_id.reference', '=', pos_order_id.picking_id.name)], limit=1)
    #         if stock_valuation_layer_id:
    #             return stock_valuation_layer_id.unit_cost
    #         return False

    def getReportData(self):
        if self.end_date < self.start_date:
            raise UserError(_('You need to select a correct starting date and ending date !'))
        start_date_to_datetime = datetime.datetime.strptime(datetime.date.strftime(self.start_date, DEFAULT_SERVER_DATE_FORMAT), DEFAULT_SERVER_DATE_FORMAT).replace(minute=0, hour=0, second=0)
        end_date_to_datetime = datetime.datetime.strptime(datetime.date.strftime(self.end_date, DEFAULT_SERVER_DATE_FORMAT), DEFAULT_SERVER_DATE_FORMAT).replace(minute=59, hour=23, second=59)
        all_pos_orders_lines = self.env['pos.order.line'].search([('order_id.date_order', '>=', start_date_to_datetime), ('order_id.date_order', '<=', end_date_to_datetime), ('order_id.state', 'not in', ['cancel'])])
        all_sale_orders_lines = self.env['sale.order.line'].search([('order_id.date_order', '>=', start_date_to_datetime), ('order_id.date_order', '<=', end_date_to_datetime), ('order_id.state', 'not in', ['cancel'])])
        products_data = {}
        categories_data = {}
        # for product in all_products_now:
        #     if not isProductAdded(products_data,product.id):
        #         addProduct(products_data, product.name, product.id, product.qty_available)
        if self.include_pos:
            for line in all_pos_orders_lines:
                if self.pricelist_ids:
                    if not line.order_id.pricelist_id:
                        continue
                    if line.order_id.pricelist_id.id not in self.pricelist_ids.ids:
                        continue
                product = line.product_id
                if not self.include_all_products:
                    if product.id not in self.product_ids.ids:
                        continue
                if not isProductAdded(products_data, product.id):
                    addProduct(products_data, product.name, product.pos_categ_id.name if product.pos_categ_id else "No Category", product.id, product.qty_available)
                if not isCategoryAdded(categories_data, product.pos_categ_id.name if product.pos_categ_id else "No Category"):
                    addCategory(categories_data, product.pos_categ_id.name if product.pos_categ_id else "No Category", 0)
                if line.qty != 0:
                    units_sold = getProductData(products_data,product.id,'units_sold')+line.qty
                    sales = getProductData(products_data,product.id,'sales')+line.price_subtotal_incl
                    categ_units_sold = getCategoryData(categories_data,product.pos_categ_id.name if product.pos_categ_id else "No Category",'units_sold')+line.qty
                    categ_sales = getCategoryData(categories_data,product.pos_categ_id.name if product.pos_categ_id else "No Category",'sales')+line.price_subtotal_incl
                    categ_qty_on_hand = getCategoryData(categories_data,product.pos_categ_id.name if product.pos_categ_id else "No Category",'qty_on_hand')+product.qty_available
                    # unit_cost = self.getUnitCostFromStockValuationLayer(is_so=False, sale_id=False, is_pos_order=True, pos_order_id=line.order_id, product_id=product)
                    # if unit_cost:
                    #     costs = getProductData(products_data, product.id, 'costs') + (unit_cost * line.qty)
                    # else:
                    costs = getProductData(products_data, product.id, 'costs') + (product.standard_price * line.qty)
                    categ_costs = getCategoryData(categories_data, product.pos_categ_id.name if product.pos_categ_id else "No Category", 'costs') + (product.standard_price * line.qty)
                    updateProductData(products_data, product.id, 'units_sold', units_sold)
                    updateProductData(products_data, product.id, 'sales', sales)
                    updateProductData(products_data, product.id, 'costs', costs)
                    updateCategoryData(categories_data, product.pos_categ_id.name if product.pos_categ_id else "No Category", 'units_sold', categ_units_sold)
                    updateCategoryData(categories_data, product.pos_categ_id.name if product.pos_categ_id else "No Category", 'sales', categ_sales)
                    updateCategoryData(categories_data, product.pos_categ_id.name if product.pos_categ_id else "No Category", 'costs', categ_costs)
                    if not isProductAdded(products_data, product.id):
                        updateCategoryData(categories_data, product.pos_categ_id.name if product.pos_categ_id else "No Category", 'qty_on_hand', categ_qty_on_hand)
        if self.include_sale:
            for line in all_sale_orders_lines:
                if self.pricelist_ids:
                    if not line.order_id.pricelist_id:
                        continue
                    if line.order_id.pricelist_id.id not in self.pricelist_ids.ids:
                        continue
                product = line.product_id
                if not self.include_all_products:
                    if product.id not in self.product_ids.ids:
                        continue
                if not isProductAdded(products_data, product.id):
                    addProduct(products_data, product.name, product.pos_categ_id.name if product.pos_categ_id else "No Category", product.id, product.qty_available)
                if not isCategoryAdded(categories_data, product.pos_categ_id.name if product.pos_categ_id else "No Category"):
                    addCategory(categories_data, product.pos_categ_id.name if product.pos_categ_id else "No Category", 0)
                if line.product_uom_qty != 0:
                    units_sold = getProductData(products_data,product.id,'units_sold')+line.product_uom_qty
                    sales = getProductData(products_data,product.id,'sales')+line.price_total
                    categ_units_sold = getCategoryData(categories_data,product.pos_categ_id.name if product.pos_categ_id else "No Category", 'units_sold')+line.product_uom_qty
                    categ_sales = getProductData(categories_data,product.pos_categ_id.name if product.pos_categ_id else "No Category",'sales')+line.price_total
                    categ_qty_on_hand = getCategoryData(categories_data,product.pos_categ_id.name if product.pos_categ_id else "No Category",'qty_on_hand')+product.qty_available
                    # unit_cost = self.getUnitCostFromStockValuationLayer(is_so=True, sale_id=line.order_id, is_pos_order=False, pos_order_id=False, product_id=product)
                    # if unit_cost:
                    #     costs = getProductData(products_data, product.id, 'costs') + (unit_cost * line.product_uom_qty)
                    # else:
                    costs = getProductData(products_data, product.id, 'costs') + (product.standard_price * line.product_uom_qty)
                    categ_costs = getCategoryData(categories_data, product.pos_categ_id.name if product.pos_categ_id else "No Category", 'costs') + (product.standard_price * line.product_uom_qty)
                    updateProductData(products_data, product.id, 'units_sold', units_sold)
                    updateProductData(products_data, product.id, 'sales', sales)
                    updateProductData(products_data, product.id, 'costs', costs)
                    updateCategoryData(categories_data, product.pos_categ_id.name if product.pos_categ_id else "No Category", 'units_sold', categ_units_sold)
                    updateCategoryData(categories_data, product.pos_categ_id.name if product.pos_categ_id else "No Category", 'sales', categ_sales)
                    updateCategoryData(categories_data, product.pos_categ_id.name if product.pos_categ_id else "No Category", 'costs', categ_costs)
                    if not isProductAdded(products_data, product.id):
                        updateCategoryData(categories_data, product.pos_categ_id.name if product.pos_categ_id else "No Category", 'qty_on_hand', categ_qty_on_hand)
        for product in products_data:
            products_data[product]['gross_profit'] = products_data[product]['sales'] - products_data[product]['costs']
            products_data[product]['percentage'] = (products_data[product]['gross_profit'] / products_data[product]['costs'])*100.0 if products_data[product]['costs'] != 0 else products_data[product]['gross_profit']
        for categ in categories_data:
            categories_data[categ]['gross_profit'] = categories_data[categ]['sales'] - categories_data[categ]['costs']
            categories_data[categ]['percentage'] = (categories_data[categ]['gross_profit'] / categories_data[categ]['costs'])*100.0 if categories_data[categ]['costs'] != 0 else categories_data[categ]['gross_profit']
        printing_date = to_tz(datetime.datetime.now(), self.tz_name)
        datas = {
            'start_date': self.start_date.strftime("%d %b %Y"),
            'end_date': self.end_date.strftime("%d %b %Y"),
            'products_data': products_data,
            'categories_data': categories_data,
            'printing_date': datetime.datetime.strftime(printing_date, DEFAULT_SERVER_DATE_FORMAT),
            'printing_time': datetime.datetime.strftime(printing_date, DEFAULT_SERVER_TIME_FORMAT),
        }
        return datas

    def submit(self):
        datas = self.getReportData()
        return self.env.ref('ywe_profit_report.stock_report_pdf').report_action(self, data=datas)

    def print_excel(self):
        # XLS report
        label_lists = ['SO', 'BARCODE', 'DEFAULTCODE', 'NAME', 'QTY', 'VENDORPRODUCTCODE', 'TITLE', 'PARTNERNAME',
                       'EMAIL', 'PHONE', 'MOBILE', 'STREET', 'STREET2', 'ZIP', 'CITY', 'COUNTRY']
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet("Profit Report")

        style1 = xlwt.easyxf('font: name Times New Roman bold on; pattern: pattern solid, fore_colour black, color white;align: horiz center;',
            num_format_str='#,##0.00')
        style2 = xlwt.easyxf('font:height 400,bold True; pattern: pattern solid, fore_colour black, color white;align: horiz center;',
                             num_format_str='#,##0.00')
        style4 = xlwt.easyxf('font:height 200,bold True; align: horiz center;', num_format_str='#,##0.00')
        style3 = xlwt.easyxf('align: horiz center;', num_format_str='#,##0.00')

        data = self.getReportData()
        sheet.write_merge(2, 3, 4, 8, 'Ywe Studio W.L.L', style2)
        sheet.write_merge(5, 5, 4, 8, 'Inventory Profitability Report', style4)
        sheet.write_merge(7, 7, 4, 5, 'For the Period From', style4)
        sheet.write_merge(7, 7, 6, 6, data['start_date'], style4)
        sheet.write_merge(7, 7, 7, 7, 'To', style4)
        sheet.write_merge(7, 7, 8, 8, data['end_date'], style4)

        sheet.write(10, 1, 'S NO', style1)
        sheet.write_merge(10, 10, 2, 3, 'Item ID', style1)
        sheet.write_merge(10, 10, 4, 4, 'Units Sold', style1)
        sheet.write_merge(10, 10, 5, 5, 'Sales($)', style1)
        sheet.write_merge(10, 10, 6, 6, 'Cost($)', style1)
        sheet.write_merge(10, 10, 7, 8, 'Profit(%)', style1)
        sheet.write_merge(10, 10, 9, 10,'Gross Profit($)', style1)
        sheet.write_merge(10, 10, 11, 12,'Quantity On Hand', style1)

        col = 1
        row = 11
        count_no = 0


        for line in data['products_data']:
            count_no += 1
            sheet.write(row, 1, str(count_no), style3)
            sheet.write_merge(row, row, 2, 3, data['products_data'][line]['name'], style3)
            sheet.write(row, 4, data['products_data'][line]['units_sold'], style3)
            sheet.write(row, 5, data['products_data'][line]['sales'], style3)
            sheet.write(row, 6, data['products_data'][line]['costs'], style3)
            sheet.write_merge(row, row, 7, 8, data['products_data'][line]['percentage'], style3)
            sheet.write_merge(row, row, 9, 10, data['products_data'][line]['gross_profit'], style3)
            sheet.write_merge(row, row, 11, 12, data['products_data'][line]['qty_on_hand'], style3)
            row+=1



        # CSV report
        datas = []

        output = StringIO()
        label = ';'.join(label_lists)
        output.write(label)
        output.write("\n")

        for data in datas:
            record = ';'.join(data)
            output.write(record)
            output.write("\n")
        data = base64.b64encode(bytes(output.getvalue(), "utf-8"))
        path = '/opt/odoo12/odoo/ywebh/'
        filename = (path+'Profitability Report' + '.xls')
        workbook.save(filename)
        fp = open(filename, "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data)

        # Files actions
        attach_vals = {
            'pr_data': 'Profitability Report' + '.xls',
            'file_name': out,
            'pr_work': 'Report' + '.csv',
            'file_names': data,
        }

        act_id = self.env['profit.report.out'].create(attach_vals)
        fp.close()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'profit.report.out',
            'res_id': act_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',
        }

class StockReportTemplate(models.AbstractModel):
    _name = 'report.ywe_profit_report.action_stock_report_template'

    def _get_report_values(self, docids, data=None):
        # for data_line in data['products_data']:
        #     print(str(data_line))
        docargs = {
                  'doc_ids': self.ids,
                  'data':data,
                }
        return docargs


class ProfitReportOut(models.Model):
    _name = 'profit.report.out'
    _description = 'Profit report'

    pr_data = fields.Char('Name', size=256)
    file_name = fields.Binary('Sale Order Excel Report', readonly=True)
    pr_work = fields.Char('Name', size=256)
    file_names = fields.Binary('Sale Order CSV Report', readonly=True)
