# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Odoo Mexico Localization for Stock/Landing',
    'summary': '''
        Generate Electronic Invoice with Customs Number
    ''',
    'version': '1.0',
    'category': 'Hidden',
    'depends': [
        'stock_landed_costs',
        'sale_management',
        'account_accountant',
        'l10n_mx_edi_customs',
    ],
    'data': [
        'views/stock_landed_cost.xml',
    ],
    'installable': True,
    'license': 'OEEL-1',
}
