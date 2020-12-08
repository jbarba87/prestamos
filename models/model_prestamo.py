from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime

class prestamo(models.Model):
  _name = 'prestamos.prestamo'
  _description = "Prestamos al asociado"
  

  # Si se cambia el socio, se debe mostrar las facturas del socio que esten abiertas
  @api.onchange('socio_id')
  def onchange_partner_id(self):
    for rec in self:
      #return {'domain': {'factura': [( 'partner_id', '=', rec.socio_id.id), ('state', '=', 'open')]}}
      rec.orden = ""
      return {'domain': {'orden': [( 'partner_id', '=', rec.socio_id.id), ('state', '=', 'sale')]}}

  interes = fields.Float(string="TEA (%)")
  cuotas = fields.Selection([
    ('12', '12'),
    ('24', '24'),
    ('36', '36'),
  ], default="12", string="Número de cuotas")

  # Restringir a los partner con el check de socio
  socio_id = fields.Many2one('res.partner', string="Socio")

  # Restring las facturas abiertas del socio 
  #factura = fields.Many2one('account.invoice', string="Factura", domain="[('state', '=', 'open')]")
  orden = fields.Many2one('sale.order', string="Orden de venta")
  cuota = fields.Float(string="Monto de la cuota")

  estado = fields.Selection([
    ('Borrador', 'Borrador'),
    ('En cuotas', 'En cuotas'),
  ], default="Borrador")

  @api.one
  @api.depends('orden')
  def get_monto(self):
    if self.orden is not False:
      self.monto_prestamo = self.orden.amount_total

  #@api.onchange('orden')
  #def get_monto(self):
  #  for rec in self:
  #    self.monto_prestamo = self.orden.amount_total

  monto_prestamo = fields.Float(string="Monto del prestamo", compute="get_monto", store=True)

  def calcula_cuotas(self):
    if int(self.cuotas)!= 0:
      n = int(self.cuotas)
      self.cuota = self.orden.amount_total/n
      TEM = ((1 + self.interes/100)**(n / 360)) - 1
      self.cuota = self.orden.amount_total * ( (TEM*(1+TEM)**n) / (( ( 1 + TEM )**n) - 1 ) ) 
    else:
      raise ValidationError('Error al procesar el dato.')
    
  def desdoblar(self):
    # Cambia el estado y crea las cuotas
    if self.estado == "En cuotas":
      return
    else:
      mes_actual = datetime.now().month
      anho_actual = datetime.now().year
      dia = 14  # Dia de vencimiento
      n = int(self.cuotas)
      meses_cuotas = [ mes_actual + i for i in range(1, n + 1) ]
      anhos_cuotas = [ anho_actual for i in range(1, n + 1) ]

      # Cantidad de años
      num_anhos = int(n/12)

      # Iteramos en la cantidad años para calcular los vectores años y meses
      for i in range(num_anhos):
        for index, value in enumerate(meses_cuotas):
          #for i in range(max_anhos):
          if value > 12:
            meses_cuotas[index] = meses_cuotas[index] - 12
            anhos_cuotas[index] = anhos_cuotas[index] + 1
            value = value - 12

      fechas = []

      # Creo el string fecha con los datos de los vectores
      for index, mes in enumerate(meses_cuotas):
        #fecha = str( anhos_cuotas[index] ) + '-' + str( meses_cuotas[index] ) + '-' + str(dia)
        fecha =  str(dia) + '-' + str( meses_cuotas[index] ) + '-' + str( anhos_cuotas[index] )
        fechas.append(fecha)
      print(fechas)
      # Creacion de los records en cuotas
      for i in range(n):
        vals = {
          'vencimiento' : fechas[i],
          'numero' : i + 1,
          'monto' : self.cuota,
          'orden' : self.id,
          'estado' : 'Por pagar',
        }
        self.env['prestamos.cuota'].create(vals)

      # cambiamos el estado de la orden de venta y el estado actual
      self.orden.state = "done"
      self.estado = "En cuotas"

    # end else

  lista_cuotas = fields.One2many('prestamos.cuota', 'orden', string="Cuotas")