# -*- coding: utf-8 -*-
from odoo import http

# class AzBrcAttendance(http.Controller):
#     @http.route('/az__brc_attendance/az__brc_attendance/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/az__brc_attendance/az__brc_attendance/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('az__brc_attendance.listing', {
#             'root': '/az__brc_attendance/az__brc_attendance',
#             'objects': http.request.env['az__brc_attendance.az__brc_attendance'].search([]),
#         })

#     @http.route('/az__brc_attendance/az__brc_attendance/objects/<model("az__brc_attendance.az__brc_attendance"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('az__brc_attendance.object', {
#             'object': obj
#         })