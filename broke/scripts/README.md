# Public-data export workflow

A reviewed export script is not implemented yet. Do not place the private workbook or raw finance records in this repository.

When implementing the workflow, it must:
1. Read source data from a local/private path outside the repository.
2. Produce only approved aggregate fields matching `data/public.json`.
3. Refuse to output identifying creditor, account, or transaction-level information.
4. Validate date formats, currency, totals, and null/missing values.
5. Write a preview to a temporary location for manual review before publishing.
6. Require an explicit approval step before updating `data/public.json`.

Until those checks exist, edit the public template only with manually reviewed, approved aggregate values.
