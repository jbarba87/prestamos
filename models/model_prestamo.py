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
      rec.orden = ""
      #return {'domain': {'orden': [( 'partner_id', '=', rec.socio_id.id), ('state', '=', 'sale')]}} # Orden de venta 1
      return {'domain': {'orden': [( 'partner_id', '=', rec.socio_id.id), ('state', '=', 'open')]}} # Factura


  interes = fields.Float(string="TEA (%)", default=8.00)
  cuotas = fields.Selection([
    ('12', '12'),
    ('24', '24'),
    ('36', '36'),
  ], default="12", string="Número de cuotas")

  # Restringir a los partner con el check de socio
  socio_id = fields.Many2one('res.partner', string="Socio")

  # Restring las facturas abiertas del socio 
  orden = fields.Many2one('account.invoice', string="Factura", domain="[('state', '=', 'open')]")
  #orden = fields.Many2one('sale.order', string="Orden de venta") # ------> 2
  cuota = fields.Monetary(string="Monto de la cuota")

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
  currency_id = fields.Many2one("res.currency", string="Moneda", default=163)
  monto_prestamo = fields.Monetary(string="Monto del prestamo", compute="get_monto", store=True)

  def calcula_cuotas(self):
    if int(self.cuotas)!= 0:
      n = int(self.cuotas)
      self.cuota = self.orden.amount_total/n
      TEM = ((1 + self.interes/100)**(1 / 12)) - 1
      self.cuota = self.orden.amount_total * ( (TEM*(1+TEM)**n) / (( ( 1 + TEM )**n) - 1 ) ) 
      print(TEM)
      print(self.cuota)
    else:
      raise ValidationError('Error al procesar el dato.')
    
  def desdoblar(self):
    # Cambia el estado y crea las cuotas
    if self.estado == "En cuotas":
      raise ValidationError('Error, al parecer la factura ya se encuentra en cuotas.')

      return
    else:
      mes_actual = datetime.now().month
      anho_actual = datetime.now().year

      # Seleccion del dia de vencimiento, si no se ha elegido, se elegira 14
      if self.dia_vencimiento is not False:
        dia = self.dia_vencimiento
      else:
        dia = 14

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
      #self.orden.state = "done" # ------> 3
      self.orden.state = "in_payment"
      self.estado = "En cuotas"

    # end else

  lista_cuotas = fields.One2many('prestamos.cuota', 'orden', string="Cuotas")

  dia_vencimiento = fields.Selection([(x, str(x)) for x in range(5, 25)], default="14", string="Dia Vencimiento")