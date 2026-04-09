---
title: Mortgage Payment
summary: Monthly payment for a fixed-rate amortizing mortgage.
inputs: [principal, rate, years]
labels: ["Principal ($)", "Annual rate (%)", "Amortization (years)"]
defaults: [400000, 5, 25]
formula: "(principal * (rate / 100 / 12)) / (1 - Math.pow(1 + rate / 100 / 12, -years * 12))"
output: "Monthly payment: $ {result}"
---

Standard amortizing mortgage payment. Does not include property taxes or insurance. Compare the result against the cash flow ceiling from the Cash Flow Strategy plan section before acting on it.
