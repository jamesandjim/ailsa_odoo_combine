# -*- coding: utf-8 -*-

from odoo import api, models, fields


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    l10n_mx_edi_payment_method_id = fields.Many2one(
        'l10n_mx_edi.payment.method',
        string='Payment Way',
        help='Indicates the way the payment was/will be received, where the '
        'options could be: Cash, Nominal Check, Credit Card, etc.')

    def process_reconciliation(self, counterpart_aml_dicts=None,
                               payment_aml_rec=None, new_aml_dicts=None):
        invoice_ids = []
        for aml_dict in counterpart_aml_dicts or []:
            if aml_dict['move_line'].invoice_id:
                invoice_ids.append(aml_dict['move_line'].invoice_id.id)
        res = super(AccountBankStatementLine, self.with_context(
            l10n_mx_edi_manual_reconciliation=False)).process_reconciliation(
                counterpart_aml_dicts=counterpart_aml_dicts,
                payment_aml_rec=payment_aml_rec, new_aml_dicts=new_aml_dicts)
        if not self.l10n_mx_edi_is_required():
            return res
        payments = res.mapped('line_ids.payment_id').filtered(
            lambda x: x.l10n_mx_edi_pac_status != 'signed')
        payment_data = self._l10n_mx_edi_get_payment_extra_data(invoice_ids)
        # Avoid overwriting the payment method of the payment
        pay_no_method = payments.filtered(lambda p: not p.l10n_mx_edi_payment_method_id)
        pay_no_method.write(payment_data)
        payment_data.pop('l10n_mx_edi_payment_method_id', None)
        (payments - pay_no_method).write(payment_data)
        payments._l10n_mx_edi_retry()
        return res

    @api.multi
    def l10n_mx_edi_is_required(self):
        self.ensure_one()
        # TODO remove this crappy hack and make a bridge module for l10n_mx_edi and point_of_sale
        if getattr(self, 'pos_statement_id', False):
            # payments from pos not must generate payment complement: pos is tolerated not supported
            return False
        version = self.env['account.invoice'].l10n_mx_edi_get_pac_version()
        country = self.env.ref('base.mx')
        return version == '3.3' and self.company_id.country_id == country

    def _l10n_mx_edi_get_payment_extra_data(self, invoice_ids=None):
        self.ensure_one()
        payment_method = self.l10n_mx_edi_payment_method_id.id or self.journal_id.l10n_mx_edi_payment_method_id.id
        result = {
            'l10n_mx_edi_payment_method_id': payment_method,
            'invoice_ids': [(4, inv) for inv in invoice_ids],
        }
        return result