from odoo import fields, models, api


class MedicalAppointmentExt(models.Model):
    _inherit = 'medical.appointment'
    _description = 'Medical Appointment Extension'

    # lines for dental services page on notebook
    dental_services_ids = fields.One2many('dental.services.lines', 'dental_services_id')

    # lines for dental measurement page on notebook
    dental_measurement_ids = fields.One2many('dental.measurement.lines', 'dental_measurement_id')

    # flag field for consultation service to ve dentist
    is_service_dentist = fields.Boolean(compute='_is_service_dentist', sanitize=False)

    # method for visibility of dental services page
    def _is_service_dentist(self):
        for rec in self:
            if rec.consultations_id.name == 'Dentist':
                rec.is_service_dentist = True
            else:
                rec.is_service_dentist = False


class DentalServicesLines(models.Model):
    _name = 'dental.services.lines'
    _description = 'Dental Service Lines'

    # Line fields
    services_id = fields.Many2one('product.template')
    service_cost = fields.Float(related='services_id.list_price', store=True)

    # Inverse name
    dental_services_id = fields.Many2one('medical.appointment')


class DentalMeasurementLines(models.Model):
    _name = 'dental.measurement.lines'
    _rec_name = 'patient_id'
    _description = 'Dental Measurement Lines'

    # Jaw and teeth selection fields
    selection_jaw = fields.Selection(
        [('urj', 'Upper Right Jaw'), ('lrj', 'Lower Right Jaw'), ('ulj', 'Upper Left Jaw'), ('llj', 'Lower Left Jaw')])

    # relation with data model
    measure_data_ids = fields.Many2many('dental.measure.data')
    patient_id = fields.Many2one('medical.patient', 'Patient')
    patient_name = fields.Char()
    start_date = fields.Date('Start Date', default=fields.Date.context_today)
    insertion_date = fields.Date('Insertion Date')
    state = fields.Selection([('pending', 'Pending'),
                              ('done', 'Done')], default='pending')
    # Other info
    patient_contact = fields.Char()
    cost = fields.Float()

    # inverse name
    dental_measurement_id = fields.Many2one('medical.appointment')

    # decorator/method for value return according to jaw selected
    @api.onchange('selection_jaw')
    def which_select_teeth(self):
        if self.selection_jaw:
            self.write({"measure_data_ids": False})
            return {
                'domain': {
                    'measure_data_ids': [('selection_jaw', '=', self.selection_jaw)]
                }
            }

    @api.onchange('patient_id')
    def update_patient_name(self):
        for rec in self:
            rec.write({'patient_id': self.dental_measurement_id.patient_id.id,
                       'patient_name': self.dental_measurement_id.patient_id.patient_id.name})


class DentalMeasurementData(models.Model):
    _name = "dental.measure.data"
    _description = 'Dental Measurement Data'

    # fields for jaw_data.xml for values of selection
    name = fields.Char()
    selection_jaw = fields.Selection(
        [('urj', 'Upper Right Jaw'), ('lrj', 'Lower Right Jaw'), ('ulj', 'Upper Left Jaw'), ('llj', 'Lower Left Jaw')])
