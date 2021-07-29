const path = require("path");

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
