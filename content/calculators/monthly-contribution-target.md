---
title: Monthly Contribution for a Goal
summary: Monthly amount required to reach a target amount at a given return.
inputs: [target, rate, years]
labels: ["Target amount ($)", "Annual rate (%)", "Years"]
defaults: [100000, 5, 20]
formula: "target * (rate / 100 / 12) / (Math.pow(1 + rate / 100 / 12, years * 12) - 1)"
output: "Required monthly contribution: $ {result}"
---

Solves the future-value-of-an-annuity formula for the monthly payment. Assumes contributions at the end of each month and a constant return.
