from odoo import fields, models, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class InstallmentsPaymentWizard(models.TransientModel):
    _name = 'installments.payment'
    _description = 'Installment of Payments'

    number_of_invoices = fields.Integer(string='Number of Installments')
    last_date = fields.Date()

    def create_installments(self):
        if self.number_of_invoices:
            current_active_id = self.env.context.get('active_id')
            dentist_receptionist = self.env['dentist.receptionist'].search([('id', '=', current_active_id)])
            sale_journals = self.env['account.journal'].search([('type', '=', 'sale')])
            invoice_ids = []
            start = datetime.today().date()
            invoice_dates = []
            for day in range(self.number_of_invoices):
                date = (start + relativedelta(months=day)).isoformat()
                invoice_dates.append(date)
            for invoice_date in invoice_dates:
                date_obj = datetime.strptime(invoice_date, "%Y-%m-%d").date()
                create_invoice = self.env['account.move'].create({
                    'invoice_origin': dentist_receptionist.appointments_id.name or '',
                    'move_type': 'out_invoice',
                    'journal_id': sale_journals and sale_journals[0].id or False,
                    'partner_id': dentist_receptionist.appointments_id.patient_id.patient_id.id,
                    'dental_appointment_id': dentist_receptionist.id or False,
                    'company_id': self.env.company.id,
                    'medical_invoice_type': "services",
                    'invoice_date_due': date_obj,
                    'invoice_date': datetime.today().date(),
                })
                product = []
                for rec in dentist_receptionist.appointments_id.dental_services_ids:
                    if rec:
                        product.append(
                            (0, 0, {'product_id': rec.services_id.product_variant_id.id,
                                    'price_unit': rec.service_cost / self.number_of_invoices}))
                # for tooth in dentist_receptionist.appointments_id.dental_measurement_ids:
                #     if tooth:
                #         teeth_sides = " ".join([jaw for jaw in self._tooth_jaws(tooth.selection_jaw)])
                #         product.append((0, 0, {
                #             'product_id': self.env.ref('dentist_management.teeth_data_product').product_variant_id.id,
                #             'name': teeth_sides + " " + (
                #                 ' '.join(tooth.measure_data_ids.mapped('name'))),
                #             'price_unit': tooth.cost / self.number_of_invoices}))
                create_invoice.write({'invoice_line_ids': product})
                invoice_ids.append(create_invoice.id)
                if create_invoice.id:
                    dentist_receptionist.installment_check = True
                if date_obj == datetime.today().date():
                    create_invoice.write({'state': 'posted'})

    @staticmethod
    def _tooth_jaws(jaw):
        if jaw == 'urj':
            yield 'Upper Right Jaw: '
        elif jaw == 'lrj':
            yield 'Lower Right Jaw: '
        elif jaw == 'ulj':
            yield 'Upper Left Jaw: '
        elif jaw == 'llj':
            yield 'Lower Left Jaw: '
