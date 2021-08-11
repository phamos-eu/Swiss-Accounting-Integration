# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe
from .utils import get_aggregated_transaction, get_individual_transation
import frappe
import datetime
import cgi
from os import path

__version__ = '0.0.1'


@frappe.whitelist()
def create_abacus_export(start_date, end_date, is_aggregated):
    """
    return xml Template to Download
    if Aggregated is Required ?
    """
    if is_aggregated:
        return get_aggregated_transaction(start_date, end_date)
    else:
        return get_individual_transation(start_date, end_date)


@frappe.whitelist()
def gl():
    """
    The Getting the GL Entry and Creating
    the Data Structure
    """

    entries = frappe.db.get_list('GL Entry',
                                 fields=["*"],
                                 filters={
                                     'posting_date': ['>=', '08-09-2021']
                                 })
    for entry in entries:
        entryLevel = 'A'
        entryType = 'S'
        type = 'Normal'
        debit_or_credit = 'C' if entry.credit > 0 else 'D'
        client = 0
        division = 0
        document_no = entry.name
        date = entry.posting_date
        value_date = entry.posting_date
        doc = frappe.get_doc(entry.voucher_type, entry.voucher_no)
        keyCurrency = doc.party_account_currency
        currency = doc.currency
        amount = doc.total
        keyAmount = 123
        account = 133
        # Tax Account
        taxAccount = 1330
        # Posting Text
        text = 1
        # No of Single Elements
        single_count = 12

    # Single Information
    entryType = 'A'
    debit_or_credit = 'D'
    entry_date = '28-01-12'
    value_date = '28-01-12'
    currency = 'CHF'
    amount = 129
    keyAmount = 123
    account = 1222
    text = 'a'
    document_no = 1233
    taxdata = {
        'taxIncluded': 'I',
        'taxType': 1,
        'useCode': 0,
        'currency': 'CHF',
        'amount': 0,
        'keyAmount': -359.44,
        'taxRate': 8,
        'taxCoefficient': 100,
        'taxCode': 111,
        'flatRate': 0
    }


@frappe.whitelist()
def gl2():
    """
    Aggregation Not Working
    """

    transactions = []
    # TODO: Get Currency From Options
    company = 'Grynn Advanced'
    baseCurrency = frappe.get_value('Company', company, 'default_currency')

    invoices = frappe.get_list('Sales Invoice', filters={
        'posting_date': ['>=', '08-09-2021']
    })

    for invoice in invoices:
        inv = frappe.get_doc('Sales Invoice', invoice.name)
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
                'account': getAccountNumber(inv.debit_to),
                'amount': inv.base_grand_total,
                'singles': [{
                    'account':  getAccountNumber(item.income_account),
                    'amount': inv.base_net_total,
                    'currency': inv.currency
                }],
                'debit_credit': 'D',
                'date': datetime.datetime.now(),
                'currency': inv.currency,
                'tax_account':   getAccountNumber(taxAccount) or None,
                'tax_amount': inv.total_taxes_and_charges or None,
                'tax_rate': rate or None,
                'tax_code': tax_code or "312",
                'tax_currency': baseCurrency,
                'text1': inv.name
            })

    # Purchase Invoice

    purchaseInvoices = frappe.get_list('Purchase Invoice', filters={
        'posting_date': ['>=', '08-09-2021']
    })

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
                'singles': [{
                    'account':  getAccountNumber(item.expense_account),
                    'amount': inv.base_net_total,
                    'currency': inv.currency
                }],
                'debit_credit': 'C',
                'date': datetime.datetime.now(),
                'currency': inv.currency,
                'tax_account':   getAccountNumber(taxAccount) or None,
                'tax_amount': inv.total_taxes_and_charges or None,
                'tax_rate': rate or None,
                'tax_code': tax_code or "312",
                'tax_currency': baseCurrency,
                'text1': inv.name
            })

    # Payment Entry

    paymentEntry = frappe.get_list('Payment Entry', filters={
        'posting_date': ['>=', '08-09-2021']
    })

    for invoice in paymentEntry:
        inv = frappe.get_doc('Payment Entry', invoice.name)
        transactions.append({
            'account': getAccountNumber(inv.paid_from),
            'amount': inv.paid_amount,
            'singles': [{
                'account':  getAccountNumber(inv.paid_to),
                'amount': inv.paid_amount,
                'currency': inv.paid_to_account_currency
            }],
            'debit_credit': 'C',
            'date': datetime.datetime.now(),
            'currency': inv.paid_from_account_currency,
            'tax_account': None,
            'tax_amount': None,
            'tax_rate': None,
            'tax_code': None,
            'text1': inv.name
        })

    # Journal Entry

    journalEntry = frappe.get_list('Journal Entry', filters={
        'posting_date': ['>=', '08-09-2021']
    })

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

    content = frappe.render_template(
        path.join(path.dirname(__file__), 'abacus.html'), data)

    return {'content': content}


def getAccountNumber(account_name):
    """
    Get Account Number
    or None
    """
    if account_name:
        return frappe.get_value('Account', account_name, 'account_number')
    else:
        return None
