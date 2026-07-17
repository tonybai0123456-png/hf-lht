# BUW AIOS Architecture

## Mission
Build a company operating system in which ChatGPT acts as the coordination layer across management, marketing, retail, CRM, Shopify, development, customer service, and data.

## Operating principles
1. Slack is the operational communication layer.
2. GitHub is the controlled change-management layer.
3. Business systems remain the source of truth for transactions.
4. AI Agents analyze, prepare, route, and monitor work.
5. High-risk actions require human approval.
6. Every important task should have an owner, status, evidence, and next action.

## Core layers
- Experience layer: ChatGPT Work, Slack
- Agent layer: CEO, Marketing, Retail, CRM, Shopify, Developer, Data, Customer Service
- Workflow layer: Issues, approvals, SOPs, automations
- Knowledge layer: strategy, product knowledge, SOPs, meeting records
- Data layer: Shopify, CRM, POS, ads, social, inventory, finance
- Control layer: permissions, audit trails, branch protection, privacy rules

## Standard work loop
Request -> Agent triage -> Task record -> Human approval when required -> Execution -> Validation -> Reporting -> Knowledge update

## Human approval required
- Production deployments
- Main branch merges
- Payment or checkout changes
- Bulk customer-data changes
- Deletion of business records
- Large outbound customer campaigns
- Permission, credential, or security changes
- Material pricing, coupon, or financial-rule changes

## Current implementation order
1. Governance and Agent charters
2. GitHub and Slack operating standards
3. Company knowledge base
4. Shopify and CRM integration
5. POS, social, advertising, and inventory integration
6. CEO dashboards and exception monitoring
7. Semi-automated and automated operating loops
