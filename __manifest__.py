# -*- coding: utf-8 -*-
{
    'name': "Dentist Management",  # Module title
    'summary': "Manage Dental Services",  # Module subtitle phrase
    'description': """
Manage Dental Services
==============
Description related to Dentist.
    """,
    'author': "Sufyan Butt - AxiomWorld",
    'website': "http://www.axiomworld.net",
    'category': 'Healthcare',
    'version': '15.0.0.0.1',
    'depends': ['healthcare_management'],

    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'data/product_data.xml',
        'data/jaw_data.xml',
        'wizard/installments_payment_wizard.xml',
        'views/dentist_receptionist.xml',
        # 'views/dentist.xml',
        'views/medical_appointment_ext.xml',
        'views/dental_measurement_lines.xml',

    ],

}
