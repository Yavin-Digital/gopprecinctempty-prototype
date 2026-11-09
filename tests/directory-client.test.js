const assert = require("assert");
const fs = require("fs");
const path = require("path");

global.document = { getElementById: undefined };
eval(fs.readFileSync(path.join(__dirname, "../js/directory.js"), "utf8"));

const rows = [
  { precinct: "4043", status: "chair listed in Nov 7 roster" },
  { precinct: "4165", status: "labeled vacant in Nov 7 roster" },
  { precinct: "4196", status: "chair listed in Nov 7 roster" }
];
assert.strictEqual(DirectoryFilter.filterRows(rows, "", "labeled vacant in Nov 7 roster").length, 1);
assert.strictEqual(DirectoryFilter.filterRows(rows, "4196", "").length, 1);
assert.strictEqual(DirectoryFilter.filterRows(rows, "4043", "labeled vacant in Nov 7 roster").length, 0);
console.log("directory filter tests passed");
