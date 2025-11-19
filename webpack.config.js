const path = require("path");
const crypto = require("crypto");

const crypto_orig_createHash = crypto.createHash;
crypto.createHash = algorithm => crypto_orig_createHash(algorithm == "md4" ? "sha256" : algorithm);

module.exports = {
  entry: "./src/index.js",
  output: {
    path: path.resolve(
      __dirname,
      "swiss_accounting_integration",
      "public",
      "js"
    ),
    filename: "index.js",
  },
};
