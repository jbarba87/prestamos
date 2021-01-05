# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class cuota(models.Model):
  _name = 'prestamos.cuota'

  monto = fields.Float(string="Monto")
  estado = fields.Selection([
    ('Por pagar', 'Por pagar'),
    ('Pagada', 'Pagada'),
    ('Vencida', 'Vencida'),
  ], string="Estado", compute="get_estado")
  numero = fields.Integer(string="Numero de cuota")
  vencimiento = fields.Date(string="Vencimiento")
  orden = fields.Many2one('prestamos.prestamo', string="Orden de venta")
  pagada = fields.Boolean(default=False)
  no_vencida = fields.Boolean(default=False, compute="cuota_activa") # indica si estamos en el mes de paga
  activa = fields.Boolean(default=False, compute="activate")

  tipo_pago = fields.Selection([
    ('Fibra', 'Fibra'),
    ('Efectivo', 'Efectivo'),
  ], default="Fibra", string="Tipo de pago")

  # Funcion del boton pagar
  def reg_pago(self):
    self.pagada = True
    print("Pago registrado")

  @api.one
  @api.depends('vencimiento', 'estado')
  def get_estado(self):
    if self.pagada == True:
      self.estado = 'Pagada'
      return

    if self.vencimiento is not False:
      fecha_actual = datetime.today().date()

      if (fecha_actual > self.vencimiento) and (self.pagada == False):
        self.estado = 'Vencida'
      else:
        self.estado = 'Por pagar'

  @api.one
  @api.depends('vencimiento')
  def cuota_activa(self):
    if self.vencimiento.month == datetime.now().month and self.vencimiento.year == datetime.now().year:
      self.no_vencida = True

  @api.one
  @api.depends('no_vencida', 'pagada')
  def activate(self):
    if not self.pagada and self.no_vencida:
      self.activa = True