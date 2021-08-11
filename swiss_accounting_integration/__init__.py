# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe
import cgi
from werkzeug.wrappers import Response

__version__ = '0.0.1'


@frappe.whitelist()
def gl(company):
    """
    Abacus XML
    """

    transactions = []

    baseCurrency = frappe.get_value('Company', company, 'default_currency')

    invoices = docs('Sales Invoice')

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

        for item in inv.items:
            transactions.append({
                'account': getAccountNumber(inv.debit_to),
                'amount': inv.base_grand_total,
                'against_singles': [{
                    'account':  getAccountNumber(item.income_account),
                    'amount': inv.base_net_total,
                    'currency': inv.currency
                }],
                'debit_credit': 'D',
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

    # Purchase Invoice

    purchaseInvoices = docs('Purchase Invoice')

    for invoice in purchaseInvoices:
        inv = frappe.get_doc('Purchase Invoice', invoice.name)
        if inv.taxes_and_charges:
            tax_record = frappe.get_doc(
                "Sales Taxes and Charges Template", inv.taxes_and_charges)
            tax_code = 312  # tax_record.tax_code
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

    paymentEntry = docs('Payment Entry')

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

    journalEntry = docs('Journal Entry')

    for invoice in journalEntry:
        inv = frappe.get_doc('Journal Entry', invoice.name)

        if inv.accounts[0].debit_in_account_currency != 0:
            debit_credit = "D"
            amount = inv.accounts[0].debit_in_account_currency
        else:
            debit_credit = "C"
            amount = inv.accounts[0].credit_in_account_currency
            # create content
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
        'transactions': transactions
    }

    content = frappe.render_template('abacus.html', data)

    # Response

    resp = Response()
    resp.mimetype = 'text/xml'
    resp.charset = 'utf-8'
    resp.data = content

    return resp


def getAccountNumber(account_name):
    """
    Get Account Number
    or None
    """
    if account_name:
        return frappe.get_value('Account', account_name, 'account_number')
    else:
        return None


def docs(doc):
    return frappe.get_list(doc, filters={
        'posting_date': ['>=', '08-09-2021']
    })
