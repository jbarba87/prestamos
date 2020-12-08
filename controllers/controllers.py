# -*- coding: utf-8 -*-
from odoo import http

# class Prestamos(http.Controller):
#     @http.route('/prestamos/prestamos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/prestamos/prestamos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('prestamos.listing', {
#             'root': '/prestamos/prestamos',
#             'objects': http.request.env['prestamos.prestamos'].search([]),
#         })

#     @http.route('/prestamos/prestamos/objects/<model("prestamos.prestamos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('prestamos.object', {
#             'object': obj
#         })