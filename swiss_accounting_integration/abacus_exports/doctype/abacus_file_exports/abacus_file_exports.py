# -*- coding: utf-8 -*-
# Copyright (c) 2021, Grynn and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
# import frappe
from frappe.model.document import Document


class AbacusFileExports(Document):
    def submit(self):
        '''
        On Submit Hook
        Check out 
        https://frappeframework.com/docs/user/en/basics/doctypes/controllers#controller-hooks
        '''
        self.get_transactions()
        return

    def get_transactions(self):
        """
        What are Transactions ?

        - Sales Invoice
        - Purchase Invoice
        - Payment Entry
        - Journal Entry
        """
        # Get Sales Invoice
        sales_invoices = frappe.db.get_list('Sales Invoice',
                                            filters={
                                                'posting_date': self.start_date,
                                                'posting_date': self.end_date,
                                                'docstatus': 1,
                                                'exported_to_abacus': 0,
                                                'company': self.Company

                                            })

        # Get Purchase Invoice
        purchase_invoice = frappe.db.get_list('Purchase Invoice',
                                              filters={
                                                  'posting_date': self.start_date,
                                                  'posting_date': self.end_date,
                                                  'docstatus': 1,
                                                  'exported_to_abacus': 0,
                                                  'company': self.Company
                                              })
        # Get Payment Entry
        payment_entry = frappe.db.get_list('Payment Entry',
                                           filters={
                                               'posting_date': self.start_date,
                                               'posting_date': self.end_date,
                                               'docstatus': 1,
                                               'exported_to_abacus': 0,
                                               'company': self.Company
                                           })
        # Get Journal Entry
        journal_entry = frappe.db.get_list('Journal Entry',
                                           filters={
                                               'posting_date': self.start_date,
                                               'posting_date': self.end_date,
                                               'docstatus': 1,
                                               'exported_to_abacus': 0,
                                               'company': self.Company
                                           })

        # Combining Entry
        docs = sales_invoices + purchase_invoice + payment_entry + journal_entry

        # clear all children
        self.references = []

        # add to child table
        for doc in docs:
            self.append('references', {'dt': doc['dt'], 'dn': doc['dn']})
        self.save()

        # mark as exported
        sinvs = self.get_docs(docs, "Sales Invoice")
        pinvs = self.get_docs(docs, "Purchase Invoice")
        pes = self.get_docs(docs, "Payment Entry")
        jvs = self.get_docs(docs, "Journal Entry")

        update_query = """UPDATE `tabSales Invoice`
                SET `tabSales Invoice`.`exported_to_abacus` = 1
                WHERE
                    `tabSales Invoice`.`name` IN ({sinvs});""".format(
            sinvs=self.get_sql_list(sinvs))
        frappe.db.sql(update_query)
        update_query = """UPDATE `tabPurchase Invoice`
                SET `tabPurchase Invoice`.`exported_to_abacus` = 1
                WHERE
                    `tabPurchase Invoice`.`name` IN ({pinvs});""".format(
            pinvs=self.get_sql_list(pinvs))
        frappe.db.sql(update_query)
        update_query = """UPDATE `tabPayment Entry`
                SET `tabPayment Entry`.`exported_to_abacus` = 1
                WHERE
                    `tabPayment Entry`.`name` IN ({pes});""".format(
            pes=self.get_sql_list(pes))
        frappe.db.sql(update_query)
        update_query = """UPDATE `tabJournal Entry`
                SET `tabJournal Entry`.`exported_to_abacus` = 1
                WHERE
                    `tabJournal Entry`.`name` IN ({jvs});""".format(
            jvs=self.get_sql_list(jvs))
        frappe.db.sql(update_query)
        return
        pass
