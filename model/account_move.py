# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    dental_appointment_id = fields.Many2one('dentist.receptionist')
