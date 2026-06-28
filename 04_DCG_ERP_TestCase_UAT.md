# 04_DCG_ERP_TestCase_UAT

Version: 1.0

# Table of Contents

1.  Test Strategy
2.  Environment
3.  SIT Checklist
4.  UAT Checklist
5.  Module Test Cases
6.  Go-live Checklist
7.  Regression Checklist
8.  Acceptance Criteria

------------------------------------------------------------------------

# 1. Test Strategy

Testing Levels

-   Unit Test
-   Integration Test (SIT)
-   User Acceptance Test (UAT)
-   Regression Test
-   Go-live Validation

------------------------------------------------------------------------

# 2. Test Environment

-   Odoo 18 Community
-   PostgreSQL
-   Test Database
-   Demo Data
-   Separate UAT Database

------------------------------------------------------------------------

# 3. SIT Checklist

## Master Data

-   Company
-   Department
-   Employee
-   Customer
-   Currency
-   Approval Matrix

Result

-   Pass
-   Fail
-   Blocked

------------------------------------------------------------------------

# 4. UAT Checklist

## CRM

-   Create Lead
-   Convert Opportunity
-   Create Proposal
-   Approval
-   Create Contract

## Contract

-   Create Contract
-   Amendment
-   Renewal
-   Expiry

## Project

-   Create Project
-   Milestone
-   Assign Resource
-   Complete Project

## Resource

-   Capacity
-   Allocation
-   Utilization

## Timesheet

-   Submit
-   Approve
-   Lock Period

## Finance

-   Revenue
-   Cost
-   Margin
-   Invoice

## Business Trip

-   Request
-   Approval
-   Expense Settlement

## Warranty

-   Create Ticket
-   SLA
-   Close Ticket

## Document

-   Upload
-   Review
-   Publish
-   Version

## HR Resource

-   Skill
-   Certificate
-   KPI

## Asset

-   Register Asset
-   Assign
-   Return
-   Maintenance

------------------------------------------------------------------------

# 5. Test Case Template

Test ID:

Module:

Title:

Pre-condition:

Test Steps:

Expected Result:

Actual Result:

Status:

Tester:

Test Date:

------------------------------------------------------------------------

# 6. Go-live Checklist

Infrastructure

-   Server Ready
-   SSL
-   Backup
-   SMTP
-   Scheduled Actions

Application

-   Modules Installed
-   Security
-   Menu
-   Reports
-   Dashboard

Business

-   Master Data Completed
-   Users Created
-   Roles Assigned
-   Opening Data Imported

Acceptance

-   UAT Approved
-   Training Completed
-   Sign-off Received

------------------------------------------------------------------------

# 7. Regression Checklist

Run after every release

-   Login
-   Dashboard
-   CRM
-   Contract
-   Project
-   Timesheet
-   Finance
-   Warranty
-   Document
-   Asset

------------------------------------------------------------------------

# 8. Acceptance Criteria

A release is accepted when

-   All Critical Test Cases Passed
-   No Critical Bug
-   UAT Approved
-   Production Checklist Completed
-   Project Manager Sign-off
-   Customer Sign-off

------------------------------------------------------------------------

# Bug Severity

Critical

High

Medium

Low

------------------------------------------------------------------------

# Test Report Summary

Total Test Cases

Passed

Failed

Blocked

Pass Rate

Bug Count

------------------------------------------------------------------------

End of Document
