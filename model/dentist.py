from odoo import models, fields, api


class Dentist(models.Model):
    _name = 'dentist'
    _rec_name = 'appointments_id'

    # created from dentist.receptionist when apt is in confirmed state
    appointments_id = fields.Many2one('medical.appointment')
    patient_name = fields.Char(related='appointments_id.patient_code', store=True)
    appointment_date = fields.Datetime(related='appointments_id.appointment_date', store=True)
    patient_status = fields.Selection(related='appointments_id.patient_status', store=True)
    validity_status = fields.Selection(related='appointments_id.validity_status', store=True)
    dental_chair = fields.Char()

    state = fields.Selection([('confirm', 'Confirmed'), ('checked', 'Checked')], default='confirm')

    # notebook fields
    prescription = fields.Html()
    lab_tests = fields.Html()

    # method for checkup done button
    def action_checkup_done(self):
        self.state = 'checked'
        rec = self.env['dentist.receptionist'].search([('appointments_id', '=', self.appointments_id.id)])
        rec.state = 'checked'
        rec.prescription = self.prescription
        rec.lab_tests = self.lab_tests
        return
