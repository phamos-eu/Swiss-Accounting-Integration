# -*- coding: utf-8 -*-
# Copyright (c) 2021, Grynn and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
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
        What is Transations 
        """
        pass
