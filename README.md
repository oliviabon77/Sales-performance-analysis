# Sales Performance and Fulfillment Analysis: 
The project was designed to mirror a real reporting workflow as much as possible, beginning with raw transactional data and ending with cleaned reporting tables and summary outputs.

## Overview

This project analyzes retail sales data and transforms it into clean reporting tables for business analysis using Python and Pandas.

The workflow includes data cleaning, validation, KPI creation, and summary reporting. In addition to preparing the data for analysis, the project explores revenue trends, fulfillment timing, discount effects, and data quality issues that could influence reporting accuracy.

---

## Business Questions Explored

- Which product categories generated the most revenue?
- Which product colors performed best each year?
- Were fulfillment lead times consistent across product categories?
- How much did discounts affect net revenue?
- Were there data quality issues that could affect reporting reliability?

---

## Key Analysis Areas

### Revenue Trends
Revenue was analyzed across product categories, years, and product colors to identify patterns in sales performance and customer purchasing behavior.

### Fulfillment Timing
Lead times between order and shipment dates were analyzed by category to explore differences in fulfillment performance across products.

### Discount Impact
The analysis compared gross revenue before discounts with net revenue after discounts to better understand how discounting affected sales performance.

### Data Quality Validation
The project also tracked issues that could affect reporting reliability, including missing values, duplicate records, invalid ship dates, and unusual discount values.

---

## Workflow

The project includes:

- Data cleaning and preprocessing
- Data type standardization
- Join validation and integrity checks
- Product master cleanup
- KPI creation
- Summary reporting table generation
- CSV export workflows

Two metrics created during the analysis include:

| Metric | Purpose |
|---|---|
| `TotalLineExtendedPrice` | Measures net revenue after discounts |
| `LeadTimeInBusinessDays` | Measures fulfillment timing |

---

## Dataset Note

The datasets used in this project are not included in the repository because they were originally provided as part of a technical assessment process.

To respect the original usage context, only the project code, workflow structure, and documentation are included here.

---

## Tools Used

- Python
- Pandas
- NumPy
- CSV data sources
- SQL-style joins and transformations

---

## Potential Next Steps

Future improvements could include:
- Building interactive dashboards for revenue and fulfillment monitoring
- Expanding the analysis using customer or regional data
- Exploring relationships between discounting and purchasing patterns
- Adding additional visualizations and reporting outputs

---

## Skills Used

Throughout this project, I worked with:
- Data cleaning and preprocessing
- ETL-style workflows
- KPI calculation
- Revenue and operational analysis
- Data validation
- Pandas transformations
- SQL-style joins
- Data quality assessment
- Python programming

---

## Why This Project Matters

This project helped me practice how technical data work connects to reporting, operations, and decision-making. In addition to cleaning and validating data, the analysis focused on identifying patterns that could influence reporting accuracy, fulfillment performance, and revenue analysis. The project also reinforced how operational and reporting decisions depend heavily on data quality and metric definition. Small issues such as inconsistent product categories, duplicate records, or incorrect date formatting can significantly change business reporting outputs and downstream analysis.

# Dataset Note

The datasets used in this project are not included in the repository because they were originally provided as part of a technical assessment process.

To respect the original usage context, only the project code, workflow structure, and documentation are included here.

