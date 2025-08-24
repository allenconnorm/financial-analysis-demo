//M script to import and clean data
//demo for Portland BES financial analyst position

let
    //import csv
    Source = Csv.Document(File.Contents("C:\Users\allen\OneDrive\Documents\GitHub\CS314-Project-A\financial-analysis-demo\sample_data\sample_budget_data.csv"), [Delimiter=",", Columns=9, Encoding=1252, QuoteStyle=QuoteStyle.None]),

    //promote headers
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),

    //change data types to have more appropriate attributes
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"Fiscal_Year", Int64.Type}, 
        {"Period", Int64.Type}, 
        {"Division_Code", type text}, 
        {"Division_Name", type text}, 
        {"Account_Code", type text}, 
        {"GL_Account_Description", type text}, 
        {"Budget_Amount", Currency.Type}, 
        {"Actual_Amount", Currency.Type}, 
        {"Transaction_Date", type date}
    }),

    //clean division names
    #"Cleaned Division Names" = Table.TransformColumns(#"Changed Type", {
        {"Division_Name", Text.Proper, type text}
    }),

    //add variance calculations
    #"Added Variance" = Table.AddColumn(#"Cleaned Division Names", "Variance",
        each [Actual_Amount] - [Budget_Amount], Currency.Type),

    #"Added Variance Percent" = Table.AddColumn(#"Added Variance", "Variance_Percent", 
        each if [Budget_Amount] = 0 then null else [Variance] / [Budget_Amount], Percentage.Type),

    //date components

    #"Added Year" = Table.AddColumn(#"Added Variance Percent", "Year", 
        each Date.Year([Transaction_Date]), Int64.Type),

    #"Added Month" = Table.AddColumn(#"Added Year", "Month", 
        each Date.Month([Transaction_Date]), Int64.Type),
    
    #"Added Quarter" = Table.AddColumn(#"Added Month", "Quarter", 
        each Date.QuarterOfYear([Transaction_Date]), Int64.Type),

    //add expense categories
    #"Added Expense Category" = Table.AddColumn(#"Added Quarter", "Expense_Category", 
        each if Text.StartsWith([Account_Code], "11") then "Personnel"
        else if Text.StartsWith([Account_Code], "21") then "Materials & Supplies"
        else if Text.StartsWith([Account_Code], "31") then "Services"
        else if Text.StartsWith([Account_Code], "41") then "Capital Outlay"
        else "Other", type text),

    //budget status
    #"Added Budget Status" = Table.AddColumn(#"Added Expense Category", "Budget_Status", 
        each if [Variance_Percent] > 0.1 then "Over Budget"
        else if [Variance_Percent] > 0.05 then "Warning"
        else if [Variance_Percent] < -0.05 then "Under Budget"
        else "On Track", type text),

    //sort data
    #"Sorted Rows" = Table.Sort(#"Added Budget Status",{
        {"Division_Code", Order.Ascending}, 
        {"Transaction_Date", Order.Descending}
    })

in 
    #"Sorted Rows"