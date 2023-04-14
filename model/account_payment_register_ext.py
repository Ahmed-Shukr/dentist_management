from odoo import fields, models, api, _


class AccountPaymentRegisterExt(models.TransientModel):
    _inherit = 'account.payment.register'

    def cancel(self):
        invoice_id = self.line_ids[0].move_id
        if invoice_id:
            if invoice_id.medical_invoice_id == "services":
                active_medical_dentist_id = self.env['dentist.receptionist'].search(
                    [('account_move_id', '=', invoice_id.id)])
                for active in active_medical_dentist_id:
                    active.write({'account_move_id': False, 'state': 'new'})
        return super().cancel()
    
    def action_create_payments(self):
        invoice_id = self.line_ids[0].move_id
        if invoice_id:
            if invoice_id.medical_invoice_type == "services":
                active_medical_dentist_id = self.env['dentist.receptionist'].sudo().search(
                    [('account_move_id', '=', invoice_id.id)])
                for active in active_medical_dentist_id:
                    if active.patient_status == 'ambulatory':
                        pass
                    else:
                        active.write({'state': 'paid'})
        return super().action_create_payments()