# Supply Chain SQL Forensics Engine

## Executive Findings Report

**Tools:** PostgreSQL, Python, Pandas, SQLAlchemy, pgAdmin, VS Code
**Datasets:** Olist Brazilian E-Commerce and BPI Challenge 2019

---

## 1. Executive Summary

This project investigates two important supply chain challenges:

1. **E-commerce delivery reliability:** Are orders arriving on time, and which regions, sellers, and product characteristics are associated with delivery problems?
2. **Procurement process efficiency:** How long does it take to receive goods, process invoices, and complete procurement activities?

I analyzed two independent public datasets using Python and PostgreSQL, performed data-quality checks, built SQL views and investigation scorecards, and evaluated database query performance.

The project provides measurable operational findings and identifies areas that warrant further business investigation.

## 2. E-Commerce Delivery Analysis — Olist

### Business Problem

An online marketplace needs to understand whether customers receive their purchases by the estimated delivery date and where late deliveries are concentrated.

### Data Analyzed

- Total orders: **99,441**
- Delivered orders: **96,478**
- Delivered orders with recorded delivery dates: **96,470**
- On-time deliveries: **89,936**
- Late deliveries: **6,534**

### Key Performance Indicators

| KPI                               |     Result |
| --------------------------------- | ---------: |
| On-time delivery rate             |     93.23% |
| Late delivery rate                |      6.77% |
| Average purchase-to-delivery time | 12.56 days |

An order was classified as late when its actual delivery date occurred after its estimated delivery date.

### Regional Findings

The following states had relatively high late-delivery rates among states with at least 300 qualifying orders:

| State         | Late-delivery rate |
| ------------- | -----------------: |
| Alagoas (AL)  |             21.41% |
| Maranhão (MA) |             17.43% |
| Sergipe (SE)  |             15.22% |
| Piauí (PI)    |             13.87% |
| Ceará (CE)    |             13.76% |

**Business insight:** Delivery reliability varies substantially by region. These differences can help determine where to investigate carrier coverage, transportation conditions, shipment characteristics, and delivery processes.

These regional patterns do not independently establish the cause of delays.

## 3. Seller and Shipping Performance

### Business Problem

Marketplace performance depends partly on sellers preparing and handing over orders within expected shipping deadlines.

### Analysis Performed

I connected order records, order items, seller identifiers, shipping-limit dates, and carrier handoff timestamps.

The analysis considered the distinction between item-level activity and unique seller-order associations to avoid double-counting.

### Findings

- Item records with recorded carrier handoff timestamps: **110,195**
- Item records handed to the carrier after the recorded shipping deadline: **10,270**
- After-deadline handoff rate: **9.32%**

A rule-based seller scorecard evaluated 627 eligible sellers:

| Seller investigation priority | Sellers |
| ----------------------------- | ------: |
| High                          |      17 |
| Medium                        |      94 |
| Low                           |     516 |

**Business insight:** Sellers with comparatively high delivery-lateness associations and shipping-deadline exceedance rates are candidates for operational review

The scorecard does not establish that individual sellers caused customer delivery delays.

## 4. Product Characteristics and Freight

### Business Problem

Physical product characteristics can influence shipping costs and delivery performance.

### Analysis Performed

I connected product weights and dimensions to order items, calculated order-level totals, and compared freight costs and delivery patterns across size and weight groups.

### Freight Findings

| Product-volume group | Average freight |
| -------------------- | --------------: |
| Small                |         R$16.50 |
| Medium               |         R$21.28 |
| Large                |         R$25.94 |
| Extra large          |         R$55.33 |

### Delivery Findings

- Orders weighing less than 1 kg had an observed late-delivery rate of approximately **6.47%**.
- Orders weighing at least 10 kg had an observed late-delivery rate of approximately **8.87%**.

**Business insight:** Larger and heavier shipments are associated with different freight and delivery outcomes. Shipment mix, geography, and carrier information should be evaluated before recommending operational changes.

## 5. Procurement Process Analysis — BPI Challenge 2019

### Business Problem

Procurement managers need to understand how purchase orders move through receiving and invoice-processing activities, and which cases require closer investigation.

### Data Engineering

I imported the procurement XES event log into PostgreSQL using Python.

The database contains separate procurement-case and procurement-event tables, allowing each case to be connected with its recorded activities.

### Dataset Summary

| Metric                            |    Result |
| --------------------------------- | --------: |
| Procurement cases                 |   251,734 |
| Procurement events                | 1,595,923 |
| Missing required event timestamps |         0 |
| Missing activities                |         0 |
| Duplicate case-event positions    |         0 |

Some historical timestamps were outside the main 2018–2019 period. These records were retained for auditability, while a defined analytical subset was used for the principal duration comparisons.

## 6. Procurement Lead-Time KPIs

### Overall Case Duration

For **251,467 cases** in the selected 2018–2019 analytical subset:

| KPI                     |          Result |
| ----------------------- | --------------: |
| Average case duration   |      69.50 days |
| Median case duration    |      64.04 days |
| P90 case duration       |     126.08 days |
| Cases exceeding 90 days | 76,419 (30.39%) |

Overall case duration measures the time from the first to the last recorded event. It should not be confused with supplier delivery time.

### Purchase Order to First Goods Receipt

For **234,229 qualifying cases**:

| KPI               |     Result |
| ----------------- | ---------: |
| Average lead time | 15.48 days |
| Median lead time  | 10.02 days |
| P90 lead time     | 34.12 days |

This measures the interval between purchase-order-item creation and the first recorded goods receipt.

The first goods receipt may represent partial receipt rather than complete fulfillment.

### Invoice Receipt to Clearing

For **183,020 qualifying cases**:

| KPI                  |     Result |
| -------------------- | ---------: |
| Average elapsed time | 48.20 days |
| Median elapsed time  | 42.07 days |
| P90 elapsed time     | 97.11 days |

This measures the interval between the first recorded invoice receipt and the first subsequent clearing event in the same procurement case.

These activity-based metrics use different qualifying populations and should not be added together to estimate an end-to-end process duration.

## 7. Procurement Process Complexity

The analysis found:

- **12,678 cases** with multiple goods receipts.
- **17,590 cases** containing quantity-change activities.
- **11,224 cases** containing price-change activities.

Among cases with goods receipts, approximately **5.41%** had more than one recorded receipt.

In the selected 2018–2019 subset, cases with multiple goods receipts had an average overall case duration of **75.79 days**, compared with **73.02 days** for cases with a single goods receipt.

Repeated activities can represent legitimate partial deliveries, service transactions, corrections, or other operational processes. They are not automatically evidence of errors.

## 8. Procurement Investigation Scorecard

### Objective

To help analysts prioritize cases for review without manually inspecting every procurement record.

### Scorecard Design

One point was assigned for each of the following:

- Overall recorded case duration greater than 90 days.
- At least one quantity or price change.
- At least one goods-receipt or invoice-receipt cancellation.

Cases were categorized as High, Medium, or Low investigation priority.

### Results

| Priority |   Cases | Percentage |
| -------- | ------: | ---------: |
| High     |  16,522 |      6.57% |
| Medium   |  76,551 |     30.44% |
| Low      | 158,394 |     62.99% |

**Business insight:** The scorecard identifies 16,522 cases displaying multiple investigation indicators, providing a manageable starting point for focused operational review.

This is a descriptive, rule-based prioritization tool—not a validated fraud-detection or predictive risk model.

## 9. PostgreSQL Performance Optimization

I evaluated a query retrieving the 100 most recent goods-receipt cancellation events.

Before creating a targeted partial index, PostgreSQL used a parallel sequential scan and sorting operation.

After creating the index, PostgreSQL used an index scan.

| Measurement    |     Before |    After |
| -------------- | ---------: | -------: |
| Execution time | 692.982 ms | 4.235 ms |

The observed execution-time reduction was approximately **99.39%** in this local before-and-after comparison.

Because these were individual measurements, additional benchmarking would be necessary to establish a repeatable improvement under production conditions.

## 10. Business Recommendations

**Delivery operations:** Review higher-lateness regions, taking account of shipment size, geographic characteristics, carrier capacity, and promised delivery windows.

**Seller operations:** Investigate sellers with recurring shipping-deadline exceedances, distinguishing seller preparation time from transportation time.

**Freight management:** Evaluate shipping costs across weight, volume, and geographic groups before changing packaging or logistics practices.

**Procurement operations:** Prioritize cases with combined duration, modification, and cancellation indicators, while comparing cases with similar procurement process types.

**Performance management:** Define operational service-level targets and obtain additional business context before describing observed durations as contractual breaches or inefficiencies.

## 11. Limitations

- Olist and BPI Challenge 2019 represent separate operational datasets and were not directly joined.
- Historical data shows associations, not necessarily causes.
- Procurement activity records do not always identify complete fulfillment or exact invoice-level matching.
- The procurement data contains historical timestamp anomalies.
- Investigation scorecard thresholds are illustrative.
- The database optimization result reflects a local experiment rather than a production benchmark.

## 12. Future Portfolio Extensions

The broader supply chain intelligence portfolio will explore:

- Machine learning-based demand forecasting.
- Inventory digital twins and replenishment simulation.
- Real-time logistics event streaming.
- External disruption and supply chain resilience analysis.
- Multi-agent AI decision support integrating verified analytical tools.

These extensions are planned separately and are not claimed as completed components of this project.

## Conclusion

The SQL Forensics Engine demonstrates how raw supply chain data can be transformed into reliable measurements, operational findings, investigation priorities, and reusable analytics.

The central outcome is a structured analytical foundation for understanding historical performance and supporting better-informed supply chain decisions.
