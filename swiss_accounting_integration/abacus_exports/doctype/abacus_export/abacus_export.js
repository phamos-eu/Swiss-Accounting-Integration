// Copyright (c) 2021, Grynn and contributors
// For license information, please see license.txt

frappe.ui.form.on('Abacus Export', {
	// refresh: function(frm) {

	// }
});
const attachFile = (doctype, docname, file, frm) => {
  let formData = new FormData();
  formData.append("is_private", 1);
  formData.append("folder", "Home/Attachments");
  formData.append("doctype", doctype);
  formData.append("docname", docname);
  formData.append("file", new Blob([file], { type: "text/xml" }), "abacus.xml");

  showProgress(60, "Uploading File", "Uploading File");
  fetch(FRAPPE_FILE_UPLOAD_ENDPOINT, {
    headers: {
      Accept: "application/json",
      "X-Frappe-CSRF-Token": window.frappe.csrf_token,
    },
    method: "POST",
    body: formData,
  }).then(() => {
    showProgress(100, "done", "done");
    frm.reload_doc();
  });
};
