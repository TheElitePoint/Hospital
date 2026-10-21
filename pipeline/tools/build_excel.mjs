import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const [payloadPath, outputPath] = process.argv.slice(2);
if (!payloadPath || !outputPath) throw new Error("usage: build_excel.mjs payload.json output.xlsx");
const payload = JSON.parse(await fs.readFile(payloadPath, "utf8"));
const workbook = Workbook.create();
const font = "Arial";

function scalar(value) {
  if (value === null || value === undefined) return "";
  if (Array.isArray(value) || typeof value === "object") return JSON.stringify(value);
  return value;
}

function addSheet(name, spec, tableName, accent) {
  const sheet = workbook.worksheets.add(name);
  sheet.showGridlines = false;
  const columns = spec.columns;
  const rows = spec.rows;
  const width = columns.length;
  const endCol = columnName(width);
  sheet.getRange(`A1:${endCol}1`).merge();
  sheet.getRange("A1").values = [[name]];
  sheet.getRange("A1").format = {
    font: { name: font, size: 16, bold: true, color: "#172033" },
    rowHeight: 28,
  };
  sheet.getRange(`A2:${endCol}2`).merge();
  sheet.getRange("A2").values = [[name === "People"
    ? "All unique people investigated by SOP2 and SOP3. Filter by status for the current usable pool."
    : "SOP4-selected people with all eight score components visible."]];
  sheet.getRange("A2").format = { font: { name: font, size: 10, italic: true, color: "#596579" } };
  sheet.getRange(`A3:${endCol}3`).format.fill = accent;
  sheet.getRange(`A3:${endCol}3`).format.rowHeight = 3;
  const values = [columns.map(([, label]) => label), ...rows.map(row => columns.map(([key]) => scalar(row[key])))];
  const lastRow = Math.max(4, 4 + rows.length);
  sheet.getRange(`A4:${endCol}${3 + values.length}`).values = values;
  const header = sheet.getRange(`A4:${endCol}4`);
  header.format = {
    fill: "#172033",
    font: { name: font, size: 10, bold: true, color: "#FFFFFF" },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    rowHeight: 30,
  };
  if (rows.length) {
    const body = sheet.getRange(`A5:${endCol}${4 + rows.length}`);
    body.format.font = { name: font, size: 10, color: "#253047" };
    body.format.verticalAlignment = "top";
    body.format.rowHeight = 30;
    const table = sheet.tables.add(`A4:${endCol}${4 + rows.length}`, true, tableName);
    table.style = "TableStyleMedium2";
    table.showFilterButton = true;
    table.showBandedRows = true;
  }
  sheet.freezePanes.freezeRows(4);
  sheet.freezePanes.freezeColumns(name === "People" ? 2 : 3);

  // Stable widths for normal zoom; narrative and URL fields are wider and wrapped.
  columns.forEach(([key], index) => {
    const col = sheet.getRange(`${columnName(index + 1)}:${columnName(index + 1)}`);
    let chars = 15;
    if (["full_name", "current_title", "validated_current_title", "current_company_display_name", "account_name"].includes(key)) chars = 24;
    if (["linkedin_profile_url", "missing_fact", "next_verification_action", "golden_selection_reason"].includes(key)) chars = 34;
    if (["person_id", "canonical_person_id", "account_id"].includes(key)) chars = 25;
    if (["linkedin_identity_status", "person_status", "validation_status", "validated_priority",
         "validated_commercial_role", "validated_role_family", "role_scope", "primary_use_case",
         "current_role_status", "employment_status", "linkedin_activity_status", "duplicate_status"].includes(key)) chars = 20;
    col.format.columnWidth = chars;
    if (chars >= 24) col.format.wrapText = true;
    if (key === "last_checked_at" && rows.length) {
      sheet.getRange(`${columnName(index + 1)}5:${columnName(index + 1)}${4 + rows.length}`).format.numberFormat = "yyyy-mm-dd hh:mm";
    }
  });
  if (rows.length) {
    const statusIndex = columns.findIndex(([key]) => key === (name === "People" ? "validation_status" : "validated_priority"));
    if (statusIndex >= 0) {
      const statusRange = sheet.getRange(`${columnName(statusIndex + 1)}5:${columnName(statusIndex + 1)}${4 + rows.length}`);
      statusRange.conditionalFormats.addCustom(`=${columnName(statusIndex + 1)}5="VALIDATED_PASS"`, { fill: "#DCFCE7", font: { color: "#166534", bold: true } });
      statusRange.conditionalFormats.addCustom(`=ISNUMBER(SEARCH("REVIEW",${columnName(statusIndex + 1)}5))`, { fill: "#FEF3C7", font: { color: "#92400E" } });
      statusRange.conditionalFormats.addCustom(`=ISNUMBER(SEARCH("REJECT",${columnName(statusIndex + 1)}5))`, { fill: "#FEE2E2", font: { color: "#991B1B" } });
    }
  }
  return sheet;
}

function columnName(number) {
  let name = "";
  while (number > 0) {
    number -= 1;
    name = String.fromCharCode(65 + (number % 26)) + name;
    number = Math.floor(number / 26);
  }
  return name;
}

addSheet("People", payload.people, "PeopleTable", "#2E749F");
addSheet("Golden", payload.golden, "GoldenTable", "#D39B25");
await fs.mkdir(path.dirname(outputPath), { recursive: true });
for (const sheetName of ["People", "Golden"]) {
  const preview = await workbook.render({ sheetName, range: "A1:W12", scale: 1, format: "png" });
  await fs.writeFile(path.join(path.dirname(outputPath), `${sheetName.toLowerCase()}-preview.png`),
    new Uint8Array(await preview.arrayBuffer()));
}
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);

const peopleCheck = await workbook.inspect({ kind: "table", range: "People!A1:W12", include: "values,formulas", tableMaxRows: 12, tableMaxCols: 23 });
const goldenCheck = await workbook.inspect({ kind: "table", range: "Golden!A1:W12", include: "values,formulas", tableMaxRows: 12, tableMaxCols: 23 });
const errors = await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!", options: { useRegex: true, maxResults: 100 }, summary: "formula errors" });
process.stdout.write(JSON.stringify({ outputPath, people: payload.people.rows.length, golden: payload.golden.rows.length, peopleCheck: peopleCheck.ndjson, goldenCheck: goldenCheck.ndjson, errors: errors.ndjson }));
