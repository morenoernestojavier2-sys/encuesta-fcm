function doPost(e) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var data = JSON.parse(e.postData.contents);
  
  if (data.tipo === "respuesta") {
    var sheet = ss.getSheetByName("Respuestas");
    delete data.tipo; 
    
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(Object.keys(data));
    }
    
    var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
    var rowData = [];
    for (var i = 0; i < headers.length; i++) {
      rowData.push(data[headers[i]] !== undefined ? data[headers[i]] : "");
    }
    sheet.appendRow(rowData);
  } 
  else if (data.tipo === "movimiento") {
    var sheet_mov = ss.getSheetByName("Movimientos");
    if (sheet_mov.getLastRow() === 0) {
      sheet_mov.appendRow(["Fecha_Hora", "Email_Usuario", "Seccion_Origen", "Accion"]);
    }
    sheet_mov.appendRow([data.Fecha_Hora, data.Email || "Aún no ingresado", data.Seccion_Origen, data.Accion]);
  }
  
  return ContentService.createTextOutput("OK");
}

function doGet(e) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheetName = e.parameter.sheet;
  var sheet = ss.getSheetByName(sheetName);
  var rows = sheet.getDataRange().getValues();
  var headers = rows[0];
  var jsonData = [];
  
  for (var i = 1; i < rows.length; i++) {
    var row = rows[i];
    var record = {};
    for (var j = 0; j < headers.length; j++) {
      record[headers[j]] = row[j];
    }
    jsonData.push(record);
  }
  
  return ContentService.createTextOutput(JSON.stringify(jsonData)).setMimeType(ContentService.MimeType.JSON);
}