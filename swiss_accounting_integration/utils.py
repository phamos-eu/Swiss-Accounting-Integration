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
