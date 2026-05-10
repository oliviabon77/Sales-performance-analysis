# Sales Performance and Fulfillment Analysis

## Project Overview

This project analyzes raw retail sales data and transforms it into clean, analytics-ready tables for business reporting. The goal is not only to clean the data, but also to generate insights that a business analyst could use to understand revenue performance, product trends, fulfillment speed, discount impact, and data quality risks.

The workflow uses Python and Pandas to perform an end-to-end ETL process, validate key relationships, create business metrics, and produce summary tables that could support dashboards or executive reporting.

## Business Problem

A retail company needs reliable sales data to answer questions such as:

- Which product categories are driving the most revenue?
- Which product colors perform best year over year?
- Are fulfillment lead times consistent across product categories?
- How much do discounts affect net revenue?
- Are there data quality issues that could reduce trust in reporting?

Raw sales data often contains missing values, inconsistent data types, duplicate records, and incomplete product information. Before business leaders can make decisions from the data, the data must be cleaned, validated, and transformed into usable reporting tables.

## Tools Used

- Python
- Pandas
- NumPy
- CSV data sources
- SQL-style joins and transformations

## Dataset Structure

The analysis uses three raw tables:

| Table | Description |
|---|---|
| `products.csv` | Product master data including product IDs, colors, categories, and subcategories |
| `sales_order_header.csv` | Order-level information including order dates, ship dates, freight, and salesperson IDs |
| `sales_order_detail.csv` | Line-level order details including products, quantities, prices, and discounts |

## Project Workflow

### 1. Data Loading

The raw product, sales header, and sales detail tables are loaded from the `data/` folder.

### 2. Data Type Standardization

Key fields are standardized so the data can be analyzed reliably:

- Product and order IDs are converted to numeric values
- Quantity, price, discount, and freight fields are converted to numeric values
- Order and ship dates are converted to datetime format
- Partial dates formatted as `YYYY-MM` are standardized to `YYYY-MM-01`

### 3. Data Quality Validation

The project validates core fields and table relationships before analysis.

Checks include:

- Missing or malformed product IDs
- Missing or malformed sales order IDs
- Missing or malformed order dates and ship dates
- Primary key uniqueness
- Foreign key relationships between order lines, order headers, and product records
- Join integrity checks to make sure rows are not accidentally duplicated during merges

### 4. Product Master Cleanup

The product master table is cleaned and enriched by:

- Replacing missing product colors with `N/A`
- Inferring missing product categories from subcategory values
- Labeling remaining unmapped categories as `Unknown`
- Removing duplicate product IDs by keeping the most complete record

This step improves reporting quality because product category and color are important fields for sales analysis.

### 5. Publish Table Creation

The project creates cleaned reporting tables:

| Output Table | Purpose |
|---|---|
| `publish_product.csv` | Cleaned product master table |
| `publish_orders.csv` | Cleaned order-line table with sales and fulfillment metrics |

Two key business metrics are created:

| Metric | Definition | Business Use |
|---|---|---|
| `TotalLineExtendedPrice` | `OrderQty × (UnitPrice - UnitPriceDiscount)` | Measures net revenue after discounts |
| `LeadTimeInBusinessDays` | Business days between order date and ship date | Measures fulfillment speed |

## Business Questions Answered

### 1. Which product colors generated the highest revenue each year?

The analysis identifies the top revenue-generating product color for each year. This helps the business understand customer preferences and evaluate whether certain product attributes consistently drive sales.

### 2. Which product categories generated the most revenue?

Revenue is aggregated by product category to identify the strongest-performing product groups. This can support merchandising, inventory planning, and marketing decisions.

### 3. Which product categories had the longest fulfillment times?

Average, median, and maximum business-day lead times are calculated by category. This helps identify categories that may require operational review.

### 4. How much did discounts affect revenue?

The analysis calculates gross revenue before discounts, net revenue after discounts, total discount amount, and average discount rate. This helps evaluate whether discounting may be supporting demand or reducing revenue efficiency.

### 5. What data quality issues could affect business reporting?

The project summarizes data quality risks such as missing lead times, impossible ship dates, negative revenue, zero quantity rows, and discount values greater than unit price.

## Key Business Insights

- Annual revenue analysis identifies the strongest sales year, which can be used as a benchmark for understanding product mix, customer demand, and sales performance.
- Category revenue analysis highlights which product groups contribute the largest share of revenue and may deserve priority in inventory and marketing decisions.
- Product color analysis shows whether customer preference is stable over time or changes by year.
- Lead time analysis connects sales data to operations by showing whether certain categories are slower to fulfill.
- Discount impact analysis helps evaluate the tradeoff between sales volume and revenue reduction.
- Data quality analysis shows where reporting reliability may be at risk and where better data governance is needed.

## Business Recommendations

Based on this analysis, the business could:

1. Build a recurring dashboard to monitor revenue, units sold, lead time, discount impact, and data quality issues.
2. Prioritize high-revenue categories for inventory planning and marketing review.
3. Investigate product categories with longer fulfillment times to identify supplier, inventory, or shipping bottlenecks.
4. Improve product master data governance so missing categories do not weaken reporting accuracy.
5. Monitor discounting strategy to determine whether discounts are increasing profitable demand or reducing revenue per order line.
6. Add customer, region, or sales channel data in a future version to support deeper segmentation.

## Outputs

The script exports the following CSV files to the `outputs/` folder:

| File | Description |
|---|---|
| `publish_product.csv` | Cleaned product master table |
| `publish_orders.csv` | Cleaned sales order table |
| `annual_revenue_summary.csv` | Revenue, units sold, and year-over-year trends |
| `category_revenue_summary.csv` | Revenue contribution by product category |
| `revenue_by_year_color.csv` | Revenue by product color and year |
| `top_color_by_year.csv` | Highest-revenue product color by year |
| `lead_time_by_category.csv` | Fulfillment speed by product category |
| `data_quality_summary.csv` | Data quality issue counts and rates |
| `discount_impact_summary.csv` | Gross revenue, net revenue, and discount impact |

## Skills Demonstrated

- Data cleaning
- ETL pipeline design
- Data validation
- Business analysis
- Revenue analysis
- Operational KPI analysis
- Data quality assessment
- Python programming
- Pandas transformations
- SQL-style joins
- Business insight communication

## Why This Project Matters

This project demonstrates how a data analyst can move beyond simply cleaning data and use it to support real business decisions. The analysis connects technical work to business outcomes by showing how clean data can improve reporting accuracy, identify revenue drivers, surface operational bottlenecks, and guide future dashboard development.
