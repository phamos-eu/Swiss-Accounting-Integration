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

/**
 * Creates Address Configuration
 * @param {String} currency CHF | EUR
 * @param {*} amount Amount To Pay
 * @param {String} reference Reference Code
 * @param {String} company Company Name
 * @param {Object} companyAddress Company Address
 * @param {String} companyAddressCode ALPHA-2 Address Code
 * @param {String} iban QR-IBAN
 * @param {String} customer Customer Name
 * @param {Object} customerAddress Customer Address
 * @param {String} customerAddressCode Customer Address Code
 * @returns Address Configuration
 */
export const generateQRConfig = (
  currency,
  amount,
  company,
  companyAddress,
  companyAddressCode,
  iban,
  customer,
  customerAddress,
  customerAddressCode,
  reference
) => ({
  currency,
  amount,
  reference,
  creditor: {
    name: company,
    address: companyAddress.address_line1.substring(0, 70), // Street name only
    houseNumber: companyAddress.address_line2 != null && companyAddress.address_line2.trim() !== "" ? companyAddress.address_line2.substring(0, 16) : "", // Building/house number - empty string forces Type "S"
    zip: companyAddress.pincode, // Postal code (kept as string for Type "S")
    city: companyAddress.city.substring(0, 35), // City name
    account: iban, // QR-IBAN
    country: companyAddressCode, // Country code
  },
  debtor: {
    name: customer.substring(0, 70),
    address: customerAddress.address_line1.substring(0, 70), // Street name only
    houseNumber: customerAddress.address_line2 != null && customerAddress.address_line2.trim() !== "" ? customerAddress.address_line2.substring(0, 16) : "", // Building/house number - empty string forces Type "S"
    zip: customerAddress.pincode, // Postal code (kept as string for Type "S")
    city: customerAddress.city.substring(0, 35), // City name
    country: customerAddressCode, // Country code
  },
});
