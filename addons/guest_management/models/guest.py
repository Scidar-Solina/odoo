from odoo import models, fields

class Guest(models.Model):
    _name = 'gms.guest'
    _description = 'Guest Management'

    name = fields.Char(string="First Name", required=True)
    lastName = fields.Char(string="Last Name", required=True)
    phone = fields.Char(string="Phone Number")
    email = fields.Char(string="Email")
    whoToSee = fields.Many2one('res.partner', 'Whom to See?', copy=False)
    address = fields.Char(string="Address")
    internet = fields.Boolean(string="Internet Access", store=True, readonly=False)
    purpose = fields.Char(string="Purpose of Visit")
    organization = fields.Char(string="Organization")
    otherDetails = fields.Char(string="Other Details:")
    check_in = fields.Datetime(string="Check-in Time", default=fields.Datetime.now)
    check_out = fields.Datetime(string="Check-out Time")
    room_number = fields.Char(string="Room Number")
    status = fields.Selection([
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out')
    ], default='checked_in', string="Status")
