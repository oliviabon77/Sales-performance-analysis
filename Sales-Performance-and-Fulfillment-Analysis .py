# -*- coding: utf-8 -*-
"""
Sales Performance and Fulfillment Analysis

Objective:
Transform raw retail sales data into clean analytics-ready tables and generate
business insights related to revenue, product performance, fulfillment speed,
and data quality.

This project demonstrates:
- ETL workflow design
- Data type standardization
- Primary and foreign key validation
- Product master cleanup
- Revenue and lead time metric creation
- Business analyst-style insight generation

Tools:
- Python
- Pandas
- NumPy
"""

import pandas as pd
import numpy as np


# =========================================================
# Data Loading
# =========================================================

def load_data(data_path="data"):
    """Load raw sales and product datasets."""
    products = pd.read_csv(f"{data_path}/products.csv")
    sales_header = pd.read_csv(f"{data_path}/sales_order_header.csv")
    sales_detail = pd.read_csv(f"{data_path}/sales_order_detail.csv")

    return products, sales_header, sales_detail


def review_raw_data(products, sales_header, sales_detail):
    """Print basic dataset structure and missing value counts."""
    print("\n--- Raw Data Shapes ---")
    print("Products:", products.shape)
    print("Sales Header:", sales_header.shape)
    print("Sales Detail:", sales_detail.shape)

    print("\n--- Missing Values ---")
    print("\nProducts:")
    print(products.isna().sum())

    print("\nSales Header:")
    print(sales_header.isna().sum())

    print("\nSales Detail:")
    print(sales_detail.isna().sum())


# =========================================================
# Data Cleaning and Standardization
# =========================================================

def parse_date_series(series):
    """
    Convert date fields to datetime.

    Partial dates formatted as YYYY-MM are standardized to YYYY-MM-01.
    Invalid dates are converted to NaT so they can be flagged in validation.
    """
    cleaned = series.map(lambda x: "" if pd.isna(x) else str(x)).str.strip()
    cleaned = cleaned.where(~cleaned.str.fullmatch(r"\d{4}-\d{2}"), cleaned + "-01")
    return pd.to_datetime(cleaned, format="%Y-%m-%d", errors="coerce")


def standardize_data_types(products, sales_header, sales_detail):
    """Standardize identifiers, numeric fields, and date fields."""
    products = products.copy()
    sales_header = sales_header.copy()
    sales_detail = sales_detail.copy()

    products["ProductID"] = pd.to_numeric(products["ProductID"], errors="coerce")

    sales_header["SalesOrderID"] = pd.to_numeric(
        sales_header["SalesOrderID"],
        errors="coerce"
    )

    sales_detail[["SalesOrderID", "SalesOrderDetailID", "ProductID"]] = (
        sales_detail[["SalesOrderID", "SalesOrderDetailID", "ProductID"]]
        .apply(pd.to_numeric, errors="coerce")
    )

    for col in ["OrderQty", "UnitPrice", "UnitPriceDiscount"]:
        sales_detail[col] = pd.to_numeric(sales_detail[col], errors="coerce")

    sales_header["Freight"] = pd.to_numeric(
        sales_header["Freight"],
        errors="coerce"
    )

    if "SalesPersonID" in sales_header.columns:
        sales_header["SalesPersonID"] = (
            pd.to_numeric(sales_header["SalesPersonID"], errors="coerce")
            .astype("Int64")
        )

    sales_header["OrderDate"] = parse_date_series(sales_header["OrderDate"])
    sales_header["ShipDate"] = parse_date_series(sales_header["ShipDate"])

    return products, sales_header, sales_detail


def clean_product_master(products):
    """
    Clean and enrich the product master table.

    Business rules:
    - Missing Color values are labeled as "N/A".
    - Missing ProductCategoryName values are inferred from ProductSubCategoryName.
    - Remaining unmapped categories are labeled "Unknown" to preserve order volume.
    - Duplicate ProductID rows are resolved by keeping the row with the fewest nulls.
    """
    publish_product = products.copy()

    duplicate_count = publish_product["ProductID"].duplicated().sum()
    print("\nDuplicate ProductID rows before cleanup:", int(duplicate_count))

    if duplicate_count > 0:
        publish_product = (
            publish_product
            .assign(_null_count=publish_product.isna().sum(axis=1))
            .sort_values(["ProductID", "_null_count"])
            .drop_duplicates("ProductID", keep="first")
            .drop(columns="_null_count")
            .copy()
        )

    color_nulls_before = publish_product["Color"].isna().sum()
    publish_product["Color"] = publish_product["Color"].fillna("N/A")
    color_nulls_after = publish_product["Color"].isna().sum()

    category_nulls_before = publish_product["ProductCategoryName"].isna().sum()

    subcategory = (
        publish_product["ProductSubCategoryName"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    missing_category = publish_product["ProductCategoryName"].isna()
    publish_product.loc[
        missing_category & subcategory.isin(["Gloves", "Shorts", "Socks", "Tights", "Vests"]),
        "ProductCategoryName"
    ] = "Clothing"

    missing_category = publish_product["ProductCategoryName"].isna()
    publish_product.loc[
        missing_category & subcategory.isin(["Locks", "Lights", "Headsets", "Helmets", "Pedals", "Pumps"]),
        "ProductCategoryName"
    ] = "Accessories"

    missing_category = publish_product["ProductCategoryName"].isna()
    publish_product.loc[
        missing_category & (
            subcategory.str.contains("Frames", case=False, na=False)
            | subcategory.isin(["Wheels", "Saddles"])
        ),
        "ProductCategoryName"
    ] = "Components"

    publish_product["ProductCategoryName"] = (
        publish_product["ProductCategoryName"].fillna("Unknown")
    )

    category_nulls_after = publish_product["ProductCategoryName"].isna().sum()
    unknown_category_count = (
        publish_product["ProductCategoryName"] == "Unknown"
    ).sum()

    print("\n--- Product Master Cleanup ---")
    print("Product PK unique after cleanup:", publish_product["ProductID"].is_unique)
    print("Color nulls before/after:", int(color_nulls_before), "to", int(color_nulls_after))
    print("Category nulls before/after:", int(category_nulls_before), "to", int(category_nulls_after))
    print("Unknown category count:", int(unknown_category_count))

    return publish_product


# =========================================================
# Data Validation
# =========================================================

def validate_primary_and_foreign_keys(products, sales_header, sales_detail):
    """Validate primary keys and foreign key relationships."""
    print("\n--- Primary Key Validation ---")
    print("ProductID unique:", products["ProductID"].is_unique)
    print("SalesOrderID unique:", sales_header["SalesOrderID"].is_unique)
    print("SalesOrderDetailID unique:", sales_detail["SalesOrderDetailID"].is_unique)

    missing_orders = ~sales_detail["SalesOrderID"].isin(sales_header["SalesOrderID"])
    missing_products = ~sales_detail["ProductID"].isin(products["ProductID"])

    print("\n--- Foreign Key Validation ---")
    print("Order lines with missing order header:", int(missing_orders.sum()))
    print("Order lines with missing product master:", int(missing_products.sum()))

    return {
        "missing_order_ids": int(missing_orders.sum()),
        "missing_product_ids": int(missing_products.sum())
    }


def validate_core_fields(products, sales_header, sales_detail):
    """Check for missing or malformed critical fields."""
    print("\n--- Core Field Validation ---")
    print("Bad/missing ProductIDs:", int(products["ProductID"].isna().sum()))
    print("Bad/missing SalesOrderIDs:", int(sales_header["SalesOrderID"].isna().sum()))
    print("Bad/missing SalesOrderDetailIDs:", int(sales_detail["SalesOrderDetailID"].isna().sum()))
    print("Bad/missing OrderDate:", int(sales_header["OrderDate"].isna().sum()))
    print("Bad/missing ShipDate:", int(sales_header["ShipDate"].isna().sum()))


# =========================================================
# Publish Table Creation
# =========================================================

def build_publish_orders(sales_header, sales_detail):
    """
    Build the cleaned order-level analytics table.

    Created metrics:
    - LeadTimeInBusinessDays: business days between order and ship date
    - TotalLineExtendedPrice: net revenue per order line after discount
    """
    sales_header = sales_header.copy()
    sales_detail = sales_detail.copy()

    sales_header = sales_header.rename(columns={"Freight": "TotalOrderFreight"})

    required_header_cols = [
        "SalesOrderID",
        "OrderDate",
        "ShipDate",
        "TotalOrderFreight"
    ]

    required_detail_cols = [
        "SalesOrderID",
        "SalesOrderDetailID",
        "ProductID",
        "OrderQty",
        "UnitPrice",
        "UnitPriceDiscount"
    ]

    missing_header_cols = [col for col in required_header_cols if col not in sales_header.columns]
    missing_detail_cols = [col for col in required_detail_cols if col not in sales_detail.columns]

    if missing_header_cols:
        raise KeyError(f"Missing header columns: {missing_header_cols}")

    if missing_detail_cols:
        raise KeyError(f"Missing detail columns: {missing_detail_cols}")

    publish_orders = sales_detail.merge(
        sales_header,
        on="SalesOrderID",
        how="left",
        validate="many_to_one",
        indicator=True
    )

    unmatched_headers = int((publish_orders["_merge"] == "left_only").sum())
    print("\nDetail rows with no matching header:", unmatched_headers)

    publish_orders = publish_orders.drop(columns="_merge")

    if not np.issubdtype(publish_orders["OrderDate"].dtype, np.datetime64):
        raise TypeError("OrderDate must be datetime64 before calculating lead time.")

    if not np.issubdtype(publish_orders["ShipDate"].dtype, np.datetime64):
        raise TypeError("ShipDate must be datetime64 before calculating lead time.")

    publish_orders["LeadTimeInBusinessDays"] = pd.Series(
        pd.NA,
        index=publish_orders.index,
        dtype="Int64"
    )

    valid_date_mask = (
        publish_orders["OrderDate"].notna()
        & publish_orders["ShipDate"].notna()
    )

    order_dates = publish_orders.loc[valid_date_mask, "OrderDate"].values.astype("datetime64[D]")
    ship_dates = publish_orders.loc[valid_date_mask, "ShipDate"].values.astype("datetime64[D]")

    publish_orders.loc[valid_date_mask, "LeadTimeInBusinessDays"] = (
        np.busday_count(order_dates, ship_dates).astype("int64")
    )

    publish_orders["TotalLineExtendedPrice"] = (
        publish_orders["OrderQty"]
        * (publish_orders["UnitPrice"] - publish_orders["UnitPriceDiscount"])
    )

    detail_cols = list(sales_detail.columns)
    header_cols = [col for col in sales_header.columns if col != "SalesOrderID"]

    publish_orders = publish_orders[
        detail_cols
        + header_cols
        + ["LeadTimeInBusinessDays", "TotalLineExtendedPrice"]
    ].copy()

    print("\n--- Publish Orders Summary ---")
    print("publish_orders shape:", publish_orders.shape)
    print("Null lead time rows:", int(publish_orders["LeadTimeInBusinessDays"].isna().sum()))
    print("Negative revenue rows:", int((publish_orders["TotalLineExtendedPrice"] < 0).sum()))

    return publish_orders


def run_data_quality_checks(publish_orders, publish_product, sales_header, sales_detail):
    """Run quality checks on the final analytics table."""
    print("\n--- Data Quality Checks ---")

    orphan_products = ~publish_orders["ProductID"].isin(publish_product["ProductID"])
    orphan_orders = ~sales_detail["SalesOrderID"].isin(sales_header["SalesOrderID"])

    print(
        f"Order lines with missing product master: "
        f"{int(orphan_products.sum())} ({orphan_products.mean() * 100:.2f}%)"
    )

    print(
        f"Order lines with missing order header: "
        f"{int(orphan_orders.sum())} ({orphan_orders.mean() * 100:.2f}%)"
    )

    row_count_changed = len(publish_orders) != len(sales_detail)

    print(
        f"Row count detail: {len(sales_detail)} | "
        f"publish_orders: {len(publish_orders)} | "
        f"multiplied? {row_count_changed}"
    )

    null_lead_time = publish_orders["LeadTimeInBusinessDays"].isna()
    ship_before_order = publish_orders["ShipDate"] < publish_orders["OrderDate"]
    long_lead_time = publish_orders["LeadTimeInBusinessDays"] > 60

    zero_quantity = publish_orders["OrderQty"] == 0
    negative_unit_price = publish_orders["UnitPrice"] < 0
    negative_discount = publish_orders["UnitPriceDiscount"] < 0
    discount_exceeds_price = publish_orders["UnitPriceDiscount"] > publish_orders["UnitPrice"]

    negative_revenue = publish_orders["TotalLineExtendedPrice"] < 0
    zero_revenue = publish_orders["TotalLineExtendedPrice"] == 0
    negative_revenue_positive_quantity = negative_revenue & (publish_orders["OrderQty"] > 0)

    quality_summary = pd.DataFrame({
        "Check": [
            "Null lead time",
            "Ship date before order date",
            "Lead time greater than 60 business days",
            "Zero quantity",
            "Negative unit price",
            "Negative discount",
            "Discount greater than unit price",
            "Negative revenue",
            "Zero revenue",
            "Negative revenue with positive quantity"
        ],
        "IssueCount": [
            int(null_lead_time.sum()),
            int(ship_before_order.sum()),
            int(long_lead_time.sum()),
            int(zero_quantity.sum()),
            int(negative_unit_price.sum()),
            int(negative_discount.sum()),
            int(discount_exceeds_price.sum()),
            int(negative_revenue.sum()),
            int(zero_revenue.sum()),
            int(negative_revenue_positive_quantity.sum())
        ],
        "IssueRate": [
            null_lead_time.mean(),
            ship_before_order.mean(),
            long_lead_time.mean(),
            zero_quantity.mean(),
            negative_unit_price.mean(),
            negative_discount.mean(),
            discount_exceeds_price.mean(),
            negative_revenue.mean(),
            zero_revenue.mean(),
            negative_revenue_positive_quantity.mean()
        ]
    })

    print("\nQuality Summary:")
    print(quality_summary)

    return quality_summary


# =========================================================
# Business Analysis
# =========================================================

def analyze_top_color_by_year(publish_orders, publish_product):
    """Identify the highest-revenue product color for each order year."""
    color_analysis = publish_orders.merge(
        publish_product[["ProductID", "Color"]],
        on="ProductID",
        how="left",
        validate="many_to_one"
    )

    missing_color_count = color_analysis["Color"].isna().sum()
    print("\nOrders with missing color after product join:", int(missing_color_count))

    color_analysis = color_analysis.dropna(subset=["OrderDate"])
    color_analysis["OrderYear"] = color_analysis["OrderDate"].dt.year

    revenue_by_year_color = (
        color_analysis
        .groupby(["OrderYear", "Color"], as_index=False)
        .agg(
            TotalRevenue=("TotalLineExtendedPrice", "sum"),
            OrderLines=("SalesOrderDetailID", "count"),
            UnitsSold=("OrderQty", "sum")
        )
    )

    max_revenue_by_year = (
        revenue_by_year_color
        .groupby("OrderYear", as_index=False)["TotalRevenue"]
        .max()
        .rename(columns={"TotalRevenue": "MaxRevenue"})
    )

    top_color_by_year = (
        revenue_by_year_color
        .merge(max_revenue_by_year, on="OrderYear")
        .query("TotalRevenue == MaxRevenue")
        .drop(columns="MaxRevenue")
        .sort_values(["OrderYear", "Color"])
        .reset_index(drop=True)
    )

    print("\n--- Top Color by Revenue Each Year ---")
    print(top_color_by_year)

    return revenue_by_year_color, top_color_by_year


def analyze_lead_time_by_category(publish_orders, publish_product):
    """Calculate fulfillment speed by product category."""
    category_analysis = publish_orders.merge(
        publish_product[["ProductID", "ProductCategoryName"]],
        on="ProductID",
        how="left",
        validate="many_to_one"
    )

    missing_category_count = category_analysis["ProductCategoryName"].isna().sum()
    print("\nRows with missing category after product join:", int(missing_category_count))

    category_analysis["ProductCategoryName"] = (
        category_analysis["ProductCategoryName"].fillna("Unknown")
    )

    lead_time_by_category = (
        category_analysis
        .groupby("ProductCategoryName", as_index=False)
        .agg(
            AvgLeadTimeInBusinessDays=("LeadTimeInBusinessDays", "mean"),
            MedianLeadTimeInBusinessDays=("LeadTimeInBusinessDays", "median"),
            MaxLeadTimeInBusinessDays=("LeadTimeInBusinessDays", "max"),
            LinesWithLeadTime=("LeadTimeInBusinessDays", "count"),
            TotalOrderLines=("ProductID", "size")
        )
        .sort_values("AvgLeadTimeInBusinessDays", ascending=False)
        .reset_index(drop=True)
    )

    print("\n--- Lead Time by Product Category ---")
    print(lead_time_by_category)

    return lead_time_by_category


def analyze_annual_revenue(publish_orders):
    """Analyze annual revenue, order volume, units sold, and average order-line value."""
    annual_revenue = publish_orders.dropna(subset=["OrderDate"]).copy()
    annual_revenue["OrderYear"] = annual_revenue["OrderDate"].dt.year

    annual_summary = (
        annual_revenue
        .groupby("OrderYear", as_index=False)
        .agg(
            TotalRevenue=("TotalLineExtendedPrice", "sum"),
            OrderLines=("SalesOrderDetailID", "count"),
            UnitsSold=("OrderQty", "sum"),
            AvgLineValue=("TotalLineExtendedPrice", "mean")
        )
        .sort_values("OrderYear")
        .reset_index(drop=True)
    )

    annual_summary["RevenueYoYChange"] = annual_summary["TotalRevenue"].pct_change()
    annual_summary["UnitYoYChange"] = annual_summary["UnitsSold"].pct_change()

    print("\n--- Annual Revenue Summary ---")
    print(annual_summary)

    return annual_summary


def analyze_category_revenue(publish_orders, publish_product):
    """Analyze revenue contribution by product category."""
    category_revenue = publish_orders.merge(
        publish_product[["ProductID", "ProductCategoryName"]],
        on="ProductID",
        how="left",
        validate="many_to_one"
    )

    category_revenue["ProductCategoryName"] = (
        category_revenue["ProductCategoryName"].fillna("Unknown")
    )

    category_summary = (
        category_revenue
        .groupby("ProductCategoryName", as_index=False)
        .agg(
            TotalRevenue=("TotalLineExtendedPrice", "sum"),
            OrderLines=("SalesOrderDetailID", "count"),
            UnitsSold=("OrderQty", "sum"),
            AvgLineValue=("TotalLineExtendedPrice", "mean")
        )
        .sort_values("TotalRevenue", ascending=False)
        .reset_index(drop=True)
    )

    total_revenue = category_summary["TotalRevenue"].sum()
    category_summary["RevenueShare"] = category_summary["TotalRevenue"] / total_revenue

    print("\n--- Category Revenue Summary ---")
    print(category_summary)

    return category_summary


def analyze_discount_impact(publish_orders):
    """Analyze discounting behavior and its revenue impact."""
    discount_analysis = publish_orders.copy()

    discount_analysis["GrossLineRevenue"] = (
        discount_analysis["OrderQty"] * discount_analysis["UnitPrice"]
    )

    discount_analysis["DiscountAmount"] = (
        discount_analysis["OrderQty"] * discount_analysis["UnitPriceDiscount"]
    )

    discount_analysis["DiscountRate"] = np.where(
        discount_analysis["GrossLineRevenue"] != 0,
        discount_analysis["DiscountAmount"] / discount_analysis["GrossLineRevenue"],
        np.nan
    )

    summary = pd.DataFrame({
        "Metric": [
            "Gross revenue before discounts",
            "Net revenue after discounts",
            "Total discount amount",
            "Average discount rate",
            "Discounted order-line count"
        ],
        "Value": [
            discount_analysis["GrossLineRevenue"].sum(),
            discount_analysis["TotalLineExtendedPrice"].sum(),
            discount_analysis["DiscountAmount"].sum(),
            discount_analysis["DiscountRate"].mean(),
            int((discount_analysis["UnitPriceDiscount"] > 0).sum())
        ]
    })

    print("\n--- Discount Impact Summary ---")
    print(summary)

    return summary


# =========================================================
# Business Insight Generation
# =========================================================

def generate_business_insights(
    annual_summary,
    category_summary,
    top_color_by_year,
    lead_time_by_category,
    quality_summary,
    discount_summary
):
    """Generate written business insights from the analysis outputs."""
    insights = []

    top_revenue_year = annual_summary.loc[
        annual_summary["TotalRevenue"].idxmax()
    ]

    top_category = category_summary.loc[
        category_summary["TotalRevenue"].idxmax()
    ]

    slowest_category = lead_time_by_category.loc[
        lead_time_by_category["AvgLeadTimeInBusinessDays"].idxmax()
    ]

    largest_quality_issue = quality_summary.sort_values(
        "IssueCount",
        ascending=False
    ).iloc[0]

    insights.append(
        f"Annual revenue peaked in {int(top_revenue_year['OrderYear'])}, "
        f"with total revenue of ${top_revenue_year['TotalRevenue']:,.2f}. "
        f"This year should be reviewed as a benchmark for sales performance, "
        f"product mix, and customer demand."
    )

    insights.append(
        f"{top_category['ProductCategoryName']} generated the highest category revenue "
        f"at ${top_category['TotalRevenue']:,.2f}, representing "
        f"{top_category['RevenueShare'] * 100:.1f}% of total revenue. "
        f"This category appears to be a major revenue driver and may deserve priority "
        f"in inventory planning, merchandising, and marketing analysis."
    )

    insights.append(
        f"The slowest fulfillment category was {slowest_category['ProductCategoryName']}, "
        f"with an average lead time of "
        f"{slowest_category['AvgLeadTimeInBusinessDays']:.2f} business days. "
        f"If this category also contributes meaningful revenue or order volume, "
        f"it may be a good candidate for operational review."
    )

    insights.append(
        f"The largest data quality issue was '{largest_quality_issue['Check']}', "
        f"affecting {int(largest_quality_issue['IssueCount'])} rows. "
        f"This matters because unresolved data quality issues can distort reporting, "
        f"reduce trust in dashboards, and lead to poor business decisions."
    )

    discount_amount = discount_summary.loc[
        discount_summary["Metric"] == "Total discount amount",
        "Value"
    ].iloc[0]

    insights.append(
        f"Total discount impact was ${discount_amount:,.2f}. "
        f"Discounting should be monitored because it can increase sales volume while "
        f"also reducing margin. A next-step analysis should compare discount rates "
        f"against units sold and revenue growth."
    )

    if not top_color_by_year.empty:
        repeated_colors = top_color_by_year["Color"].value_counts()
        most_common_top_color = repeated_colors.idxmax()
        top_color_years = repeated_colors.max()

        insights.append(
            f"{most_common_top_color} was the top revenue-generating color in "
            f"{top_color_years} year(s). Repeated color-level performance may indicate "
            f"stable customer preference and could inform product assortment decisions."
        )

    print("\n--- Business Insights ---")
    for i, insight in enumerate(insights, start=1):
        print(f"{i}. {insight}")

    return insights


def generate_recommendations():
    """Provide business analyst-style recommendations based on the project."""
    recommendations = [
        "Build a recurring dashboard to track revenue, units sold, lead time, and data quality issues by month.",
        "Investigate high-revenue product categories to understand whether performance is driven by volume, pricing, or product mix.",
        "Review categories with longer fulfillment times to identify possible inventory, supplier, or shipping bottlenecks.",
        "Improve product master data governance so missing categories do not weaken reporting accuracy.",
        "Monitor discounting strategy to determine whether discounts are increasing profitable demand or simply reducing revenue per order line.",
        "Add customer, region, or channel data in a future version to support deeper segmentation and sales strategy decisions."
    ]

    print("\n--- Recommendations ---")
    for i, recommendation in enumerate(recommendations, start=1):
        print(f"{i}. {recommendation}")

    return recommendations


# =========================================================
# Export Outputs
# =========================================================

def export_outputs(
    publish_product,
    publish_orders,
    annual_summary,
    category_summary,
    revenue_by_year_color,
    top_color_by_year,
    lead_time_by_category,
    quality_summary,
    discount_summary,
    output_path="outputs"
):
    """Export cleaned tables and analysis outputs as CSV files."""
    import os

    os.makedirs(output_path, exist_ok=True)

    publish_product.to_csv(f"{output_path}/publish_product.csv", index=False)
    publish_orders.to_csv(f"{output_path}/publish_orders.csv", index=False)
    annual_summary.to_csv(f"{output_path}/annual_revenue_summary.csv", index=False)
    category_summary.to_csv(f"{output_path}/category_revenue_summary.csv", index=False)
    revenue_by_year_color.to_csv(f"{output_path}/revenue_by_year_color.csv", index=False)
    top_color_by_year.to_csv(f"{output_path}/top_color_by_year.csv", index=False)
    lead_time_by_category.to_csv(f"{output_path}/lead_time_by_category.csv", index=False)
    quality_summary.to_csv(f"{output_path}/data_quality_summary.csv", index=False)
    discount_summary.to_csv(f"{output_path}/discount_impact_summary.csv", index=False)

    print(f"\nOutputs exported to the '{output_path}' folder.")


# =========================================================
# Main Pipeline
# =========================================================

def main():
    products, sales_header, sales_detail = load_data()

    review_raw_data(products, sales_header, sales_detail)

    products, sales_header, sales_detail = standardize_data_types(
        products,
        sales_header,
        sales_detail
    )

    validate_core_fields(products, sales_header, sales_detail)
    validate_primary_and_foreign_keys(products, sales_header, sales_detail)

    publish_product = clean_product_master(products)
    publish_orders = build_publish_orders(sales_header, sales_detail)

    quality_summary = run_data_quality_checks(
        publish_orders,
        publish_product,
        sales_header,
        sales_detail
    )

    annual_summary = analyze_annual_revenue(publish_orders)

    category_summary = analyze_category_revenue(
        publish_orders,
        publish_product
    )

    revenue_by_year_color, top_color_by_year = analyze_top_color_by_year(
        publish_orders,
        publish_product
    )

    lead_time_by_category = analyze_lead_time_by_category(
        publish_orders,
        publish_product
    )

    discount_summary = analyze_discount_impact(publish_orders)

    generate_business_insights(
        annual_summary,
        category_summary,
        top_color_by_year,
        lead_time_by_category,
        quality_summary,
        discount_summary
    )

    generate_recommendations()

    export_outputs(
        publish_product,
        publish_orders,
        annual_summary,
        category_summary,
        revenue_by_year_color,
        top_color_by_year,
        lead_time_by_category,
        quality_summary,
        discount_summary
    )


if __name__ == "__main__":
    main()
