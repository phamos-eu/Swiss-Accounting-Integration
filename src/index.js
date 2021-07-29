/*! *****************************************************************************
Copyright (c) Grynn GmbH. All rights reserved.
Licensed under the GPL, Version 3.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at https://www.gnu.org/licenses/gpl-3.0.en.html

THIS CODE IS PROVIDED ON AN *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
MERCHANTABLITY OR NON-INFRINGEMENT.

***************************************************************************** */
import { createQRBill } from "./createqrbill";
import { getReferenceCode } from "./utils";

window.frappe.ui.form.on("Sales Invoice", {
  on_submit: (frm) => {
    createQRBill(frm);
  },

  onload: (frm) => {
    frm.doc.esr_reference_code = "";
  },

  before_submit: (frm) => {
    const reference = getReferenceCode(frm.doc.name);
    frm.doc.esr_reference_code = reference;
  },
  refresh: (frm) => {
    frm.add_custom_button("Create QR Bill", function () {
      createQRBill(frm);
    });
  },
});
