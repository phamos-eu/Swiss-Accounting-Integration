import frappe

# Scheme of Working
# Add button to
#  - Sales Invoice
#  - Payment Entry
#  -


# Algorithm
# There are 2 kinds of Exports for abacus
# 1. Aggregated
# 2. Individual Transations

# Algorithm for Individual Transactions


def get_individual_transation(self, doc, company):
    currency = doc.company_currency()
    transactions = []
    pass


# Algorithm for Aggregated Transactions
def get_aggregated_transaction(self, doc, company):
    transactions = []
    sales_invoice = frappe.db.get_list('Sales Invoice', filters={
        'start_date': doc.date_start,
        'end_date': doc.end_date
    })
    base_currency = frappe.get_value(
        'Company', doc.company, 'default_currency')

    for invoice in sales_invoice:
        if invoice.tax_and_charges:
            tax = frappe.get_doc(
                'Sales Taxes and Charges Template', invoice.taxes_and_charges)
            tax_code = tax.tax_code
        else:
            tax_code = None

        transactions.append({
            'account': self.get_account_number(invoice.debit_to),
            'amount': invoice.debit,
            'against_singles': [{
                'account': self.get_account_number(invoice.income_account),
                'amount': invoice.income,
                'currency': invoice.currency
            }],
            'debit_credit': "D",
            'date': self.to_date,
            'currency': invoice.currency,
            'tax_account': self.get_account_number(invoice.account_head) or None,
            'tax_amount': invoice.tax or None,
            'tax_rate': invoice.rate or None,
            'tax_code': tax_code or "312",
            'tax_currency': base_currency,
            'text1': invoice.name
        })
