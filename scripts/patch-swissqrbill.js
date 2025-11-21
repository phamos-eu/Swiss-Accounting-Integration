#!/usr/bin/env node
/**
 * Patches SwissQRBill library to always use Type "S" (structured) format
 * This ensures zip code and city are always separate fields in QR code
 */

const fs = require('fs');
const path = require('path');

const filesToPatch = [
  'node_modules/swissqrbill/lib/swissqrbill.js',
  'node_modules/swissqrbill/lib/browser.js'
];

function patchFile(filePath) {
  if (!fs.existsSync(filePath)) {
    console.log(`⚠️  File not found: ${filePath}`);
    return false;
  }

  let content = fs.readFileSync(filePath, 'utf8');
  let patched = false;

  // Patch creditor section - remove Type K, always use Type S
  const creditorOld = /\/\/-- Creditor\s+if \(this\._data\.creditor\.houseNumber !== undefined\) \{[\s\S]+?\}\s+qrString \+= "\\n" \+ this\._data\.creditor\.country;/;
  const creditorNew = `//-- Creditor
        // ALWAYS USE TYPE S (STRUCTURED) - PATCHED FOR MANDATORY SEPARATE FIELDS
        // Address Type
        qrString += "\\nS";
        // Name
        qrString += "\\n" + this._data.creditor.name;
        // Address
        qrString += "\\n" + this._data.creditor.address;
        // House number (empty string if not provided)
        qrString += "\\n" + (this._data.creditor.houseNumber !== undefined ? this._data.creditor.houseNumber : "");
        // Zip (ALWAYS SEPARATE)
        qrString += "\\n" + this._data.creditor.zip;
        // City (ALWAYS SEPARATE)
        qrString += "\\n" + this._data.creditor.city;
        // Country
        qrString += "\\n" + this._data.creditor.country;`;

  if (creditorOld.test(content)) {
    content = content.replace(creditorOld, creditorNew);
    patched = true;
  }

  // Patch debtor section - remove Type K, always use Type S
  const debtorOld = /\/\/-- Debtor\s+if \(this\._data\.debtor !== undefined\) \{\s+if \(this\._data\.debtor\.houseNumber !== undefined\) \{[\s\S]+?\/\/ Country\s+qrString \+= "\\n" \+ this\._data\.debtor\.country;\s+\}/;
  const debtorNew = `//-- Debtor
        if (this._data.debtor !== undefined) {
            // ALWAYS USE TYPE S (STRUCTURED) - PATCHED FOR MANDATORY SEPARATE FIELDS
            // Address type
            qrString += "\\nS";
            // Name
            qrString += "\\n" + this._data.debtor.name;
            // Address
            qrString += "\\n" + this._data.debtor.address;
            // House number (empty string if not provided)
            qrString += "\\n" + (this._data.debtor.houseNumber !== undefined ? this._data.debtor.houseNumber : "");
            // Zip (ALWAYS SEPARATE)
            qrString += "\\n" + this._data.debtor.zip;
            // City (ALWAYS SEPARATE)
            qrString += "\\n" + this._data.debtor.city;
            // Country
            qrString += "\\n" + this._data.debtor.country;
        }`;

  if (debtorOld.test(content)) {
    content = content.replace(debtorOld, debtorNew);
    patched = true;
  }

  if (patched) {
    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`✅ Patched: ${filePath}`);
    return true;
  } else {
    console.log(`ℹ️  Already patched or pattern not found: ${filePath}`);
    return false;
  }
}

console.log('🔧 Patching SwissQRBill library to always use Type S format...\n');

let patchedCount = 0;
filesToPatch.forEach(file => {
  if (patchFile(file)) {
    patchedCount++;
  }
});

console.log(`\n✨ Patching complete! ${patchedCount} file(s) modified.`);
console.log('📝 QR codes will now ALWAYS use Type "S" with separate zip/city fields.\n');
