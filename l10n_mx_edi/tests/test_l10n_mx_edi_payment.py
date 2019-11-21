# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from . import common


class TestL10nMxEdiPayment(common.InvoiceTransactionCase):
    def setUp(self):
        super(TestL10nMxEdiPayment, self).setUp()
        isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= isr_tag
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })
        self.bank_journal = self.env['account.journal'].search([
            ('type', '=', 'bank')], limit=1)

    def test_invoice_multicurrency(self):
        """Create the next case, to check that payment complement is correct
            Invoice 1 - USD
            Invoice 2 - MXN
            Payment --- USD"""
        self.set_currency_rates(mxn_rate=1, usd_rate=0.05)
        invoices = self.create_invoice()
        invoices |= self.create_invoice(currency_id=self.mxn.id)
        invoices.action_invoice_open()
        self.bank_journal.currency_id = self.usd
        bank_statement = self.env['account.bank.statement'].create({
            'journal_id': self.bank_journal.id,
            'line_ids': [(0, 0, {
                'name': 'Payment',
                'partner_id': invoices[0].partner_id.id,
                'amount': invoices[0].amount_total + self.mxn.compute(
                    invoices[1].amount_total, self.usd),
                'currency_id': self.usd.id,
                'l10n_mx_edi_payment_method_id': self.payment_method_cash.id,
            })],
        })
        values = []
        lines = invoices.mapped('move_id.line_ids').filtered(
            lambda l: l.account_id.user_type_id.type == 'receivable')
        for line in lines:
            values.append({
                'credit': line.debit,
                'debit': 0,
                'name': line.name,
                'move_line': line,
            })
        bank_statement.line_ids.process_reconciliation(values)
        self.assertEquals(
            invoices.mapped('payment_ids').l10n_mx_edi_pac_status, 'signed',
            'The payment was not signed')

    def test_payment_multicurrency_writeoff(self):
        """Create a payment in USD to invoice in MXN with writeoff"""
        self.set_currency_rates(mxn_rate=1, usd_rate=0.055556)
        date_mx = self.env[
            'l10n_mx_edi.certificate'].sudo().get_mx_current_datetime()
        date = (date_mx - timedelta(days=1)).strftime(
            DEFAULT_SERVER_DATE_FORMAT)
        self.usd.rate_ids = self.rate_model.create({
            'rate': 0.05, 'name': date})
        invoice = self.create_invoice()
        invoice.date_invoice = date
        invoice.action_invoice_open()
        ctx = {'active_model': 'account.invoice', 'active_ids': [invoice.id]}
        register_payments = self.env['account.register.payments'].with_context(
            ctx).create({
                'payment_date': date_mx,
                'l10n_mx_edi_payment_method_id': self.env.ref(
                    'l10n_mx_edi.payment_method_efectivo').id,
                'payment_method_id': self.env.ref(
                    "account.account_payment_method_manual_in").id,
                'journal_id': self.bank_journal.id,
                'communication': invoice.number,
                'amount': invoice.amount_total, })
        payment = register_payments.create_payments()
        payment = self.env['account.payment'].search(payment.get('domain', []))
        self.assertEqual(payment.l10n_mx_edi_pac_status, "signed",
                         payment.message_ids.mapped('body'))
        cfdi = payment.l10n_mx_edi_get_xml_etree()
        self.asertEquals(
            payment.l10n_mx_edi_get_payment_etree(cfdi)[0].get('ImpSaldoInsoluto'), '0.00',
            'The invoice was not marked as fully paid in the payment complement.')
