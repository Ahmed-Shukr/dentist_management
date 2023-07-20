from odoo import fields, models, api
from datetime import date
from odoo.exceptions import UserError


class DentistReceptionist(models.Model):
    _name = 'dentist.receptionist'
    _description = 'Managing Dental Services'
    _rec_name = 'seq_number'

    # sequence number
    seq_number = fields.Char(readonly=True, required=True, copy=False, default='New')

    # fields from medical.appointment
    appointments_id = fields.Many2one('medical.appointment')
    patient_name = fields.Char(related='appointments_id.patient_code', store=True)
    appointment_date = fields.Datetime(related='appointments_id.appointment_date', store=True)
    patient_status = fields.Selection(related='appointments_id.patient_status', store=True)
    validity_status = fields.Selection(related='appointments_id.validity_status', store=True)

    dental_chair = fields.Char()

    state = fields.Selection(
        [('new', 'New'), ('confirm', 'Confirm'), ('unpaid', 'Unpaid'), ('paid', 'Paid'), ('checked', 'Checked')],
        default='new')

    # notebook fields from Dentist
    prescription = fields.Html()
    lab_tests = fields.Html()
    single_payment = fields.Boolean()
    installments_payment = fields.Boolean()
    account_move_id = fields.Many2one('account.move')
    display_smart = fields.Boolean()
    installment_check = fields.Boolean()
    appointment_state = fields.Boolean(compute='_appointment_state_check')
    invoices_count = fields.Integer(string='Invoices', compute="_count_invoices")

    # method for confirm button
    def action_confirm_apt(self):
        self.state = 'confirm'
        # change = self.appointments_id.start_appointment()
        res = self.env['dentist'].create({
            'appointments_id': self.appointments_id.id,
            'dental_chair': self.dental_chair,
        })
        return res \
            # change

    # method for smart button for dentist
    def action_open_dentist(self):
        # tree_id = self.env.ref('healthcare_management.medical_appointment_tree_view').id
        # form_id = self.env.ref('dentist_management.dupli_medical_appointment_form_view').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Dentist Appointment',
            'res_model': 'medical.appointment',
            'view_mode': 'list',
            # 'views': [[tree_id, 'list'], [form_id, 'form']],
            'domain': [('id', '=', self.appointments_id.id)]
        }

    # overriding for sequence number
    @api.model
    def create(self, vals):
        vals['seq_number'] = self.env['ir.sequence'].next_by_code('dentist.receptionist')
        result = super(DentistReceptionist, self).create(vals)
        return result

    """
    ***================================================================================***
    *** 1: Dental Receptionist will create invoice of Dental services and Measurement. ***
    *** 2: Merge the Jaws and Teeth and create invoice line with cost of teeth.        ***
    ***================================================================================***
    """

    def create_invoice(self):
        if self.state == 'confirm':
            sale_journals = self.env['account.journal'].search([('type', '=', 'sale')])
            account_invoice_obj = self.env['account.move']
            invoice_vals = {
                'invoice_origin': self.appointments_id.name or '',
                'move_type': 'out_invoice',
                'journal_id': sale_journals and sale_journals[0].id or False,
                'partner_id': self.appointments_id.patient_id.patient_id.id,
                'company_id': self.env.company.id,
                'invoice_date': date.today(),
                'medical_invoice_type': "services"
            }
            res = account_invoice_obj.create(invoice_vals)
            product = []
            for rec in self.appointments_id.dental_services_ids:
                if rec:
                    product.append(
                        (0, 0, {'product_id': rec.services_id.product_variant_id.id, 'price_unit': rec.service_cost}))
            res.write({'invoice_line_ids': product})
            self.account_move_id = res.id
            if res.id:
                self.display_smart = True
            res.write({'state': 'posted'})

    """
    **==========================================================================**
    ** This is a Static Method will yield only the value of selection field.    **               
    **==========================================================================**
    """

    # @staticmethod
    # def _tooth_jaws(jaw):
    #     if jaw == 'urj':
    #         yield 'Upper Right Jaw: '
    #     elif jaw == 'lrj':
    #         yield 'Lower Right Jaw: '
    #     elif jaw == 'ulj':
    #         yield 'Upper Left Jaw: '
    #     elif jaw == 'llj':
    #         yield 'Lower Left Jaw: '

    """
    **=============================================================================================**
    ** Smart button of Invoice is visible if single payment is True.                               **                            
    ** If we click on smart button this function will call and show corresponding Posted Invoices. **
    **=============================================================================================**
    """

    def display_invoice(self):
        return {
            'type': 'ir.actions.act_window',
            'res_id': self.account_move_id.id,
            'view_mode': 'form',
            'name': ('Invoice'),
            'res_model': 'account.move'
        }

    """
    **=========================================**
    ** This method will count the invoices.    **               
    **=========================================**
    """

    def _count_invoices(self):
        for move in self:
            move.invoices_count = len(move.account_move_id)
        return True

    def installments_button(self):
        self.ensure_one()
        return {
            'name': 'Installments',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('dental_appointment_id', '=', self.id)]
        }

    def _appointment_state_check(self):
        if self.appointments_id.invoices_state == 'done':
            self.appointment_state = True
        else:
            self.appointment_state = False
