# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe
import cgi
from frappe.utils.file_manager import save_file
from werkzeug.wrappers import Response
from .utils import is_expense, get_expenses

__version__ = '0.0.2'


def gl(company, start_date, end_date):
    """
    Abacus XML
    """

    transactions = []
    doc_invoices = []

    baseCurrency = frappe.get_value('Company', company, 'default_currency')
    invoices = docs('Sales Invoice', start_date, end_date)

    for invoice in invoices:
        inv = frappe.get_doc('Sales Invoice', invoice.name)

        if inv.taxes_and_charges:
            tax_record = frappe.get_doc(
                "Sales Taxes and Charges Template", inv.taxes_and_charges)
            tax_code = getattr(tax_record, 'tax_code', 312)
            rate = tax_record.taxes[0].rate
            taxAccount = tax_record.taxes[0].account_head
        else:
            tax_code = None
            rate = 0
            taxAccount = None

        invoice = {
            'account': getAccountNumber(inv.debit_to),
            'amount': inv.base_rounded_total,
            'against_singles': [],
            'debit_credit': 'D',
            'date': inv.posting_date,
            'currency': inv.currency,
            'exchange_rate': inv.conversion_rate,
            'text1': inv.name
        }

        # Round Off Account

        if inv.rounding_adjustment:
            company = inv.company
            roundingAccount = frappe.get_doc(
                'Company', company).round_off_account

            invoice['against_singles'].append({
                'account':  getAccountNumber(roundingAccount),
                'amount': inv.rounding_adjustment,
                'currency': inv.currency,
                'tax_account':   None,
                'tax_amount': None,
                'tax_rate':  None,
                'tax_code': None,
                'tax_currency': None,
            })

        for item in inv.items:
            invoice['against_singles'].append(
                {
                    'account':  getAccountNumber(item.income_account),
                    'amount': item.net_amount + (item.net_amount * rate / 100),
                    'currency': inv.currency,
                    'tax_account':   getAccountNumber(taxAccount) if taxAccount else None,
                    'tax_amount': item.net_amount * rate / 100,
                    'tax_rate': rate or None,
                    'tax_code': tax_code or "312",
                    'tax_currency': baseCurrency,
                }
            )

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
    purchaseInvoices = docs('Purchase Invoice', start_date, end_date)

    for invoice in purchaseInvoices:
        inv = frappe.get_doc('Purchase Invoice', invoice.name)
        if inv.taxes_and_charges:
            tax_record = frappe.get_doc(
                "Sales Taxes and Charges Template", inv.taxes_and_charges)
            tax_code = getattr(tax_record, 'tax_code', 312)
            rate = tax_record.taxes[0].rate
            taxAccount = tax_record.taxes[0].account_head
        else:
            tax_code = None

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
                'tax_account':   getAccountNumber(taxAccount) or None,
                'tax_amount': inv.total_taxes_and_charges or None,
                'tax_rate': rate or None,
                'tax_code': tax_code or "312",
                'tax_currency': baseCurrency,
                'text1': inv.name
            })

    # Payment Entry

    paymentEntry = docs('Payment Entry', start_date, end_date)

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

    # Journal Entry

    journalEntry = docs('Journal Entry', start_date, end_date)

    for invoice in journalEntry:
        inv = frappe.get_doc('Journal Entry', invoice.name)

        if inv.accounts[0].debit_in_account_currency != 0:
            debit_credit = "D"
            amount = inv.accounts[0].debit_in_account_currency
        else:
            debit_credit = "C"
            amount = inv.accounts[0].credit_in_account_currency

        transaction = {
            'account': getAccountNumber(inv.accounts[0].account),
            'amount': amount,
            'against_singles': [],
            'debit_credit': debit_credit,
            'date': inv.posting_date,
            'currency': inv.accounts[0].account_currency,
            'tax_account': None,
            'tax_amount': None,
            'tax_rate': None,
            'tax_code': None,
            'text1': cgi.escape(inv.name)
        }

        if inv.multi_currency == 1:
            transaction['exchange_rate'] = inv.accounts[0].exchange_rate
            transaction['key_currency'] = inv.accounts[0].account_currency
        else:
            transaction['key_currency'] = inv.accounts[0].account_currency

        for i in range(1, len(inv.accounts), 1):

            if debit_credit == "D":
                amount = inv.accounts[i].credit_in_account_currency - \
                    inv.accounts[i].debit_in_account_currency
            else:
                amount = inv.accounts[i].debit_in_account_currency - \
                    inv.accounts[i].credit_in_account_currency

            transaction_single = {
                'account': getAccountNumber(inv.accounts[i].account),
                'amount': amount,
                'currency': inv.accounts[i].account_currency
            }

            if inv.multi_currency == 1:
                transaction_single['exchange_rate'] = inv.accounts[i].exchange_rate
                transaction_single['key_currency'] = inv.accounts[i].account_currency
            transaction['against_singles'].append(transaction_single)
        transactions.append(transaction)

    data = {
        'invoices': doc_invoices,
        'transactions': transactions
    }

    content = frappe.render_template('abacus.html', data)

    return content


def getAccountNumber(account_name):
    """
    Get Account Number
    or None
    """
    if account_name:
        return frappe.get_value('Account', account_name, 'account_number')
    else:
        return None


def docs(doc, start, end):
    "Get Docs"
    return frappe.get_list(doc, filters=[[
        'posting_date', 'between', [start, end]
    ], ['docstatus', '=', 1]])


def get_xml(content):
    """
    Create XML Response
    """
    resp = Response()
    resp.mimetype = 'text/xml'
    resp.charset = 'utf-8'
    resp.data = content
    return resp


def attach_xml(doc, event=None):
    """
    Attach XML File to Doctype
    """
    save_file('abacus.xml', gl(doc.company, doc.start_date, doc.end_date),
              doc.doctype, doc.name, is_private=True)
