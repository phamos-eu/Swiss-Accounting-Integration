# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe
from .utils import get_aggregated_transaction, get_individual_transation
import frappe

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
    The Getting the GL Entry and Creating the Data Structure
    """

    entries = frappe.db.get_list('GL Entry', fields=["*"], filters={
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

        # Customer Currency
        keyCurrency = 'CHF'
        # currency invoice
        currency = 'CHF'
        # Amount (credit or debit)
        amount = 1299
        # Amount in key Currency
        keyAmount = 123
        # Account (Debit or credit)
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
