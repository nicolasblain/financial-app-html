---
title: Compound Growth
summary: Future value of a lump sum at a compound annual rate.
inputs: [principal, rate, years]
labels: ["Principal ($)", "Annual rate (%)", "Years"]
defaults: [10000, 6, 25]
formula: "principal * Math.pow(1 + rate / 100, years)"
output: "Future value: $ {result}"
---

Shows how an amount invested today grows over time at a constant compound rate. A 6% rate roughly doubles money every 12 years (the rule of 72).
