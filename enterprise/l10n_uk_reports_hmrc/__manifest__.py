# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'UK - Accounting Reports to HMRC',
    'version': '1.1',
    'category': 'Accounting',
    'website': 'https://www.odoo.com/page/accounting',
    'description': """
        Accounting reports send to HMRC
    """,
    'depends': [
        'l10n_uk_reports'
    ],
    'data': [
        'views/views.xml',
        'views/res_users_views.xml',
        'security/ir.model.access.csv',
        'security/hmrc_security.xml',
        'wizard/hmrc_send_wizard.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'OEEL-1',
}
