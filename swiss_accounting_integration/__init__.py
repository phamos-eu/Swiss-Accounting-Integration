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
