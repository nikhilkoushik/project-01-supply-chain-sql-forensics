
# BPI Procurement Policy Category Mapping

Version: 0.1
Status: Simulated portfolio mapping

## Purpose

This document defines how source procurement item types
are mapped to internal simulated policy classifications.

The mapping is illustrative and is not an official
classification provided by BPI Challenge 2019.

## Mapping Rule

Internal classification: STD_MATERIAL

Eligible source item type:
- Standard

Excluded source item types:
- Service
- Consignment
- Third-party
- Subcontracting
- Limit

The source item category is retained as a separate
dimension, including:
- 3-way match, invoice before GR
- 3-way match, invoice after GR

## Policy Application

Policy BP-GR-001 applies only to procurement cases
classified as STD_MATERIAL under this mapping.

The policy target is:
First goods receipt within 12 calendar days of
purchase-order-item creation.

## Limitations

The source item type Standard does not independently
prove that every item is a physical material.

This classification is used only for simulated
policy evaluation and requires business-owner
validation before any real operational deployment.

Cases with missing required timestamps or without
a valid first goods receipt are not automatically
classified as compliant or noncompliant.
