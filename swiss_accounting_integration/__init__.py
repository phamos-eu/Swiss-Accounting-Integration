# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
import cgi
from frappe.utils.file_manager import save_file
from .utils import is_expense, get_expenses, getAccountNumber, docs, data, taxes, rounding_off, document_number, invoice as inv_f, amount as inv_amt

__version__ = '0.0.2'


def gl(company, start_date, end_date):
    """
    Abacus XML
    """

    transactions = []
    doc_invoices = []

    invoices = docs('Sales Invoice', start_date, end_date)
    purchaseInvoices = docs('Purchase Invoice', start_date, end_date)
    paymentEntry = docs('Payment Entry', start_date, end_date)

    # Sales Invoice

    for invoice in invoices:
        inv = frappe.get_doc('Sales Invoice', invoice.name)

        tax_code, taxAccount, rate = taxes(
            "Sales Taxes and Charges Template", inv)

        currency = frappe.get_doc('Company', inv.company).default_currency

        invoice = inv_f(inv, inv.debit_to, 'D', currency)

        # Round Off Account
        rounding_adjustment = rounding_off(inv)

        if rounding_adjustment:
            invoice['against_singles'].append(rounding_adjustment)

        # Items
        for item in inv.items:
            invoice['against_singles'].append(
                inv_amt(item, item.income_account, inv.currency,
                        taxAccount, rate, tax_code, currency)
            )

        # Taxes
        for tax in inv.taxes:
            if is_expense(tax.item_wise_tax_detail):
                for item in get_expenses(tax):
                    invoice['against_singles'].append({
                        'account':  getAccountNumber(item['account']),
                        'amount': item['amount'],
                        'currency': inv.currency,
                        'tax_account':   None,
                        'tax_amount': None,
                        'tax_rate':  None,
                        'tax_code': None,
                        'tax_currency': None,
                    })

        doc_invoices.append(invoice)

    # Purchase Invoice

    for invoice in purchaseInvoices:
        inv = frappe.get_doc('Purchase Invoice', invoice.name)

        tax_code, taxAccount, rate = taxes(inv)

        for item in inv.items:
            transactions.append({
                'account': getAccountNumber(inv.credit_to),
                'amount': inv.base_grand_total,
                'against_singles': [{
                    'account':  getAccountNumber(item.expense_account),
                    'amount': inv.base_net_total,
                    'currency': inv.currency
                }],
                'debit_credit': 'C',
                'date': inv.posting_date,
                'currency': inv.currency,
                'exchange_rate': inv.conversion_rate,
                'tax_account':   getAccountNumber(taxAccount) if taxAccount else None,
                'tax_amount': inv.total_taxes_and_charges or None,
                'tax_rate': rate or None,
                'tax_code': tax_code or "312",
                'tax_currency': baseCurrency,
                'text1': inv.name
            })

    # Payment Entry

    for invoice in paymentEntry:
        inv = frappe.get_doc('Payment Entry', invoice.name)
        transaction = {
            'account': getAccountNumber(inv.paid_from),
            'amount': inv.paid_amount,
            'against_singles': [{
                'account':  getAccountNumber(inv.paid_to),
                'amount': inv.paid_amount,
                'currency': inv.paid_to_account_currency
            }],
            'debit_credit': 'C',
            'date': inv.posting_date,
            'exchange_rate': inv.source_exchange_rate,
            'currency': inv.paid_from_account_currency,
            'tax_account': None,
            'tax_amount': None,
            'tax_rate': None,
            'tax_code': None,
            'text1': inv.name
        }

        for deduction in inv.deductions:
            transaction['against_singles'].append({
                'account': getAccountNumber(deduction.account),
                'amount': deduction.amount,
                'currency': inv.paid_to_account_currency
            })

        transactions.append(transaction)

    return frappe.render_template('abacus.html', data(doc_invoices, transactions))


def attach_xml(doc, event=None):
    """
    Attach XML File to Doctype
    """
    save_file('abacus.xml', gl(doc.company, doc.start_date, doc.end_date),
              doc.doctype, doc.name, is_private=True)
