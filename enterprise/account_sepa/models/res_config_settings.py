# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sepa_orgid_id = fields.Char(related='company_id.sepa_orgid_id', string="Identification",
        help="Identification assigned by an institution (eg. VAT number).")
    sepa_orgid_issr = fields.Char(related='company_id.sepa_orgid_issr', string="Issuer",
        help="Will appear in SEPA payments as the name of the party initiating the payment. Limited to 70 characters.")
    sepa_initiating_party_name = fields.Char(related='company_id.sepa_initiating_party_name', string="Your Company Name", help="Name of the Creditor Reference Party. Usage Rule: Limited to 70 characters in length.")
    sepa_pain_version = fields.Selection(related='company_id.sepa_pain_version', string="SEPA Pain Version",
                            help='SEPA may be a generic format, some countries differ from the SEPA recommandations made by the EPC (European Payment Councile) and thus the XML created need some tweakenings.')
