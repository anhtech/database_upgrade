
import re
import datetime
import io
import json
import operator

from odoo.addons.web.controllers.main import ExportFormat,serialize_exception
from odoo.tools.misc import str2bool, xlsxwriter, file_open
from odoo.tools.translate import _
from odoo import http
from odoo.http import content_disposition, request
from odoo.tools.misc import xlwt
from odoo.exceptions import UserError
from odoo.tools import pycompat

class ExportXlsxWriter:

    def __init__(self, field_names, row_count=0):
        self.field_names = field_names
        self.output = io.BytesIO()
        self.workbook = xlsxwriter.Workbook(self.output, {'in_memory': True})
        self.base_style = self.workbook.add_format({'text_wrap': True})
        self.header_style = self.workbook.add_format({'bold': True})
        self.header_bold_style = self.workbook.add_format({'text_wrap': True, 'bold': True, 'bg_color': '#e9ecef'})
        self.date_style = self.workbook.add_format({'text_wrap': True, 'num_format': 'yyyy-mm-dd'})
        self.datetime_style = self.workbook.add_format({'text_wrap': True, 'num_format': 'yyyy-mm-dd hh:mm:ss'})
        self.worksheet = self.workbook.add_worksheet()
        self.value = False

        if row_count > self.worksheet.xls_rowmax:
            raise UserError(_('There are too many rows (%s rows, limit: %s) to export as Excel 2007-2013 (.xlsx) format. Consider splitting the export.') % (row_count, self.worksheet.xls_rowmax))

    def __enter__(self):
        self.write_header()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def write_header(self):
        # Write main header
        for i, fieldname in enumerate(self.field_names):
            self.write(0, i, fieldname, self.header_style)
        self.worksheet.set_column(0, i, 30) # around 220 pixels

    def close(self):
        self.workbook.close()
        with self.output:
            self.value = self.output.getvalue()

    def write(self, row, column, cell_value, style=None):
        self.worksheet.write(row, column, cell_value, style)

    def write_cell(self, row, column, cell_value):
        cell_style = self.base_style

        if isinstance(cell_value, bytes):
            try:
                # because xlsx uses raw export, we can get a bytes object
                # here. xlsxwriter does not support bytes values in Python 3 ->
                # assume this is base64 and decode to a string, if this
                # fails note that you can't export
                cell_value = pycompat.to_text(cell_value)
            except UnicodeDecodeError:
                raise UserError(_("Binary fields can not be exported to Excel unless their content is base64-encoded. That does not seem to be the case for %s.") % self.field_names[column])

        if isinstance(cell_value, str):
            if len(cell_value) > self.worksheet.xls_strmax:
                cell_value = _("The content of this cell is too long for an XLSX file (more than %s characters). Please use the CSV format for this export.") % self.worksheet.xls_strmax
            else:
                cell_value = cell_value.replace("\r", " ")
        elif isinstance(cell_value, datetime.datetime):
            cell_style = self.datetime_style
        elif isinstance(cell_value, datetime.date):
            cell_style = self.date_style
        self.write(row, column, cell_value, cell_style)

class GroupExportXlsxWriter(ExportXlsxWriter):

    def __init__(self, fields, row_count=0):
        super().__init__([f['label'].strip() for f in fields], row_count)
        self.fields = fields

    def write_group(self, row, column, group_name, group, group_depth=0):
        group_name = group_name[1] if isinstance(group_name, tuple) and len(group_name) > 1 else group_name
        if group._groupby_type[group_depth] != 'boolean':
            group_name = group_name or _("Undefined")
        row, column = self._write_group_header(row, column, group_name, group, group_depth)

        # Recursively write sub-groups
        for child_group_name, child_group in group.children.items():
            row, column = self.write_group(row, column, child_group_name, child_group, group_depth + 1)

        for record in group.data:
            row, column = self._write_row(row, column, record)
        return row, column

    def _write_row(self, row, column, data):
        for value in data:
            self.write_cell(row, column, value)
            column += 1
        return row + 1, 0

    def _write_group_header(self, row, column, label, group, group_depth=0):
        aggregates = group.aggregated_values

        label = '%s%s (%s)' % ('    ' * group_depth, label, group.count)
        self.write(row, column, label, self.header_bold_style)
        for field in self.fields[1:]: # No aggregates allowed in the first column because of the group title
            column += 1
            aggregated_value = aggregates.get(field['name'])
            self.write(row, column, str(aggregated_value if aggregated_value is not None else ''), self.header_bold_style)
        return row + 1, 0


class KsChartExport(ExportFormat, http.Controller):

    def base(self, data, token):
        params = json.loads(data)
        header,chart_data = operator.itemgetter('header','chart_data')(params)
        chart_data = json.loads(chart_data)
        chart_data['labels'].insert(0,'Measure')
        columns_headers = chart_data['labels']
        import_data = []

        for dataset in chart_data['datasets']:
            dataset['data'].insert(0, dataset['label'])
            import_data.append(dataset['data'])

        return request.make_response(self.from_data(columns_headers, import_data),
            headers=[('Content-Disposition',
                            content_disposition(self.filename(header))),
                     ('Content-Type', self.content_type)],
            cookies={'fileToken': token})


class KsChartExcelExport(KsChartExport, http.Controller):

    # Excel needs raw data to correctly handle numbers and date values
    raw_data = True

    @http.route('/ks_dashboard_ninja/export/chart_xls', type='http', auth="user")
    @serialize_exception
    def index(self, data, token):
        return self.base(data, token)

    @property
    def content_type(self):
        return 'application/vnd.ms-excel'

    def filename(self, base):
        return base + '.xls'

    def from_data(self, fields, rows):
        with ExportXlsxWriter(fields, len(rows)) as xlsx_writer:
            for row_index, row in enumerate(rows):
                for cell_index, cell_value in enumerate(row):
                    xlsx_writer.write_cell(row_index + 1, cell_index, cell_value)

        return xlsx_writer.value


class KsChartCsvExport(KsChartExport, http.Controller):

    @http.route('/ks_dashboard_ninja/export/chart_csv', type='http', auth="user")
    @serialize_exception
    def index(self, data, token):
        return self.base(data, token)

    @property
    def content_type(self):
        return 'text/csv;charset=utf8'

    def filename(self, base):
        return base + '.csv'

    def from_data(self, fields, rows):
        fp = io.BytesIO()
        writer = pycompat.csv_writer(fp, quoting=1)

        writer.writerow(fields)

        for data in rows:
            row = []
            for d in data:
                # Spreadsheet apps tend to detect formulas on leading =, + and -
                if isinstance(d, str)    and d.startswith(('=', '-', '+')):
                    d = "'" + d

                row.append(pycompat.to_text(d))
            writer.writerow(row)

        return fp.getvalue()
