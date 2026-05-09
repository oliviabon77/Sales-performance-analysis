# Sales Data ETL Pipeline with Python

## Project Overview
This project transforms raw sales data into clean, structured datasets for business reporting and analysis. The workflow uses Python and pandas to standardize data types, validate relationships between tables, clean missing values, calculate business metrics, and generate revenue and fulfillment insights.

## Business Goal
The goal of this project is to create reliable analytics-ready sales data from raw product, sales order header, and sales order detail files. The final outputs help answer questions such as:

- Which product color generated the highest revenue each year?
- Which product categories had the longest average fulfillment lead times?
- Are there data quality issues such as missing product IDs, duplicate records, invalid dates, or suspicious revenue values?

## Tools Used
- Python
- pandas
- NumPy
- Google Colab
- CSV data files

## Data Sources
The pipeline expects three input files:

- `products.csv`
- `sales_order_header.csv`
- `sales_order_detail.csv`

The data files are not included in this repository because they are not mine to share.

## Key Steps

### 1. Load Raw Data
The project loads product, order header, and order detail datasets and reviews their shapes, column types, and missing values.

### 2. Standardize Data Types
The script converts IDs, quantities, prices, discounts, freight costs, and dates into consistent formats so they can be used safely in joins and calculations.

### 3. Validate Data Quality
The pipeline checks for:

- Missing or malformed primary keys
- Duplicate product IDs
- Missing foreign key matches, orphaned records 
- Invalid order or ship dates
- Negative or zero revenue rows
- Discounts greater than unit price
- Potential join multiplication issues
- Missing product classifications 

### 4. Clean and Enrich Product Data
Missing product colors are filled with `N/A`. Missing product categories are inferred from product subcategories when possible, using business rules for Clothing, Accessories, and Components.

### 5. Build Analytics-Ready Order Table
Order detail rows are joined with order header data. The project then calculates:

- `LeadTimeInBusinessDays`
- `TotalLineExtendedPrice`

These fields support operational and revenue analysis.

### 6. Generate Business Insights 
The analysis identifies:

-Revenue appeared concentrated among a small subset of product colors and categories, suggesting opportunities for targeted inventory planning and merchansizing optimization. 


## Findings 
Based on the analysis in the notebook/script:

- Red was the top revenue color in 2021.
- Black was the top revenue color in 2022 and 2023.
- Yellow was the top revenue color in 2024.
- Average lead time was generally consistent across product categories, around 5 business days.
- A large number of rows still had unknown product category values, showing a realistic data quality limitation.

## Why This Project Matters
The transformed dataset supports data driven decision making around product preformance, fufilment efficency and revenue trends. 

## Repository Structure

```text
sales-etl-sql-python/
├── README.md
├── sales_etl_sql_python.py
├── requirements.txt
└── .gitignore
```


## Skills Demonstrated
- ETL workflow development
- Data cleaning
- Data validation
- pandas transformations
- Business metric creation
- Revenue analysis
- Operational lead time analysis
- Technical documentation
