import json


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
