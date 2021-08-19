import json
from werkzeug.wrappers import Response
from frappe.utils.file_manager import save_file
import frappe


def is_expense(txt):
    """
    Check Weather Entry in Tax
    is Expense or Not
    """
    js = json.loads(txt)
    values = js.values()
    for value in values:
        tax = value[0]
        return int(tax) == 0


def get_expenses(tax):
    """
    Get Expenses from tax
    """
    items = []
    js = json.loads(tax.item_wise_tax_detail)
    values = js.values()
    for item in values:
        items.append({
            'account': tax.account_head,
            'amount': item[1]
        })
    return items


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


def data(invoices, transactions):
    """
    Build Data
    """
    return {
        'invoices': invoices,
        'transactions': transactions
    }


def taxes(template, inv):
    """
    Taxes
    -----
    Get Taxes if Any
    """
    if inv.taxes_and_charges:

        tax_record = frappe.get_doc(template, inv.taxes_and_charges)
        tax_code = getattr(tax_record, 'tax_code', 312)
        rate = tax_record.taxes[0].rate
        taxAccount = tax_record.taxes[0].account_head
    else:
        tax_code = None
        taxAccount = None
        rate = 0
    return [tax_code, taxAccount, rate]


def rounding_off(inv):
    """
    Rounding Off Amount
    """
    if inv.rounding_adjustment:

        company = inv.company

        roundingAccount = frappe.get_doc(
            'Company', company).round_off_account

        return {
            'account':  getAccountNumber(roundingAccount),
            'amount': inv.rounding_adjustment,
            'keyamount': inv.base_rounding_adjustment,
            'currency': inv.currency,
            'tax_account':   None,
            'tax_amount': None,
            'tax_rate':  None,
            'tax_code': None,
            'tax_currency': None,
        }
    else:
        return None


def document_number(inv_name):
    """
    Converts
    ACC-PINV-2021-00003 => 202100003
    """
    split_inv_name = inv_name.split('-')
    join_inv_name = ''.join(split_inv_name)
    num = [i for i in join_inv_name if i.isdigit()]
    return ''.join(num)


def invoice(inv, account_number, debit_credit, key_currency):
    return {
        'account': getAccountNumber(account_number),
        'amount': round(inv.rounded_total, 2),
        'key_amount': round(inv.base_rounded_total, 2),
        'against_singles': [],
        'debit_credit': debit_credit,
        'date': inv.posting_date,
        'currency': inv.currency,
        'key_currency': key_currency,
        'exchange_rate': inv.conversion_rate,
        'text1': inv.name,
        'document_number': document_number(inv.name)
    }


def amount(item, income_account, inv_currency,  taxAccount, rate, code, tax_currency):
    """
    Amount: for items
    """
    return {
        'account':  getAccountNumber(income_account),
        'amount': round(item.net_amount + (item.net_amount * rate / 100), 2),
        'keyamount': round(item.base_net_amount + (item.base_net_amount * rate / 100), 2),
        'currency': inv_currency,
        'tax_account':   getAccountNumber(taxAccount) if taxAccount else None,
        'tax_amount': item.base_net_amount * rate / 100,
        'tax_rate': rate or None,
        'tax_code': code or "312",
        'tax_currency': tax_currency,
    }
