param(
    [string]$FilePath = "~\Desktop\My Bangle Bliss\flipkart from claude\<flipkart-catalog-file>.xls",
    [string]$DataPath = "~\Desktop\My Bangle Bliss\flipkart_ksg_rows.json",
    [string]$SheetName = "bangle_bracelet_armlet"
)

$rows = Get-Content $DataPath -Raw | ConvertFrom-Json

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

try {
    $wb = $excel.Workbooks.Open($FilePath)
    $ws = $wb.Sheets.Item($SheetName)

    # Build header-name -> column-index map from row 1
    $usedCols = $ws.UsedRange.Columns.Count
    $headerMap = @{}
    for ($c = 1; $c -le $usedCols; $c++) {
        $h = $ws.Cells.Item(1, $c).Value2
        if ($h -ne $null -and $h -ne "") {
            $headerMap[$h.ToString().Trim()] = $c
        }
    }
    Write-Output "Found $($headerMap.Count) named columns."

    $startRow = 5
    $rowIndex = $startRow
    foreach ($row in $rows) {
        $props = $row.PSObject.Properties
        foreach ($p in $props) {
            $colName = $p.Name
            $val = $p.Value
            if ($headerMap.ContainsKey($colName)) {
                $col = $headerMap[$colName]
                try {
                    $cell = $ws.Cells.Item($rowIndex, $col)
                    if ($val -is [int] -or $val -is [long] -or $val -is [double] -or $val -is [decimal]) {
                        $cell.Value2 = [double]$val
                    } else {
                        $cell.Value2 = [string]$val
                    }
                } catch {
                    Write-Output "ERROR at row=$rowIndex col=$col ($colName) val='$val' type=$($val.GetType().Name): $($_.Exception.Message)"
                }
            } else {
                Write-Output "WARNING: no column found for '$colName'"
            }
        }
        $rowIndex++
    }

    $wb.Save()
    Write-Output "Saved. Wrote $($rows.Count) rows starting at row $startRow."
}
finally {
    if ($wb) { $wb.Close($true) }
    $excel.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}
