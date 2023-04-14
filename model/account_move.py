# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    dental_appointment_id = fields.Many2one('dentist.receptionist')

    def action_post(self):
        if self.medical_invoice_type == "services":
            active_dentist_id = self.env['dentist.receptionist'].search([
                ('account_move_id', '=', self.id)
            ])
            for active in active_dentist_id:
                active.write({'state': 'paid'})
        return super().action_post()