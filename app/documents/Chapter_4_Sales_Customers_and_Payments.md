# Chapter 4: Sales, Customers & Payments

## 4.1 Customer Management

Every customer relationship carries two dimensions the AI must track together: **commercial value** (how much and how often they buy) and **payment risk** (how reliably they pay). A high-value customer with poor payment discipline is not automatically a "good" customer — the relationship's true worth depends on both dimensions.

Customers should be understood along a few practical lines:
- **Order frequency and size** — regular, high-volume customers deserve priority service and closer relationship management.
- **Payment behavior** — consistency of on-time payment matters as much as order volume when judging relationship health.
- **Credit exposure** — how much the customer currently owes relative to their approved limit.
- **Tenure and history** — a long-standing customer with an isolated late payment should be treated differently from a new customer showing the same behavior.

## 4.2 Credit Limits

A credit limit exists to cap how much unpaid exposure the business is willing to carry for a given customer at any one time. It is a risk control, not a formality to be waived casually.

- **Current credit** (what a customer currently owes) should always be checked against their **credit limit** before a new order is approved.
- Approving an order that would push a customer over their limit should never happen silently — it should be flagged as an explicit exception requiring a deliberate decision, not an automatic approval.
- Credit limits should be treated as **customer-specific**, based on payment history and relationship value — a long-standing, reliable customer may reasonably justify a higher limit than a new, unproven one.
- A customer consistently operating close to their limit is a signal worth watching, even if they haven't technically breached it — it suggests either underpricing the relationship's risk or a limit that needs review.

## 4.3 Sales Workflow

1. **Order intake** — a customer places a sales order for one or more products.
2. **Credit check** — the order is checked against the customer's available credit (limit minus current exposure).
3. **Stock check** — available inventory is checked to confirm the order can be fulfilled (see Chapter 2).
4. **Reservation** — stock is reserved against the order once approved.
5. **Fulfillment** — the order is picked, delivered, and its delivery status updated.
6. **Invoicing** — the customer is billed for the order.
7. **Payment collection** — payment is tracked against the invoice until settled in full.

The AI should be able to identify which stage a given order is sitting in and flag orders stalled unusually long at any one stage — a stuck order is often the first sign of a fulfillment or payment problem before it becomes visible elsewhere.

## 4.4 Customer Relationship Best Practices

- Treat reliable, high-value customers with a lighter touch on routine friction (e.g., minor short-term overdue amounts) while still protecting the business's exposure.
- Communicate proactively when an order can't be fulfilled as expected, rather than letting the customer discover a delay on their own.
- Recognize patterns of growing order volume early — a customer scaling up may need a credit limit review before they hit friction that damages the relationship.
- Keep new customers on a more conservative footing (smaller credit limits, closer payment monitoring) until a track record is established.

## 4.5 Payment Collection

Payment collection should be proactive, not purely reactive:

- Track invoices against their due dates continuously, not just when a customer flags an issue.
- Distinguish between **partial payments** (progress, not failure) and **no payment activity** (a stronger warning sign).
- Prioritize collection effort by **exposure size and age** — a large, old overdue balance deserves more urgency than a small, recent one.
- Reconcile payments against the correct orders promptly, since misapplied payments create confusion that can mask real overdue exposure or falsely flag a paying customer as delinquent.

## 4.6 Reminder Process

A graduated reminder process protects the relationship while still applying pressure:

1. **Early/friendly reminder** — sent shortly after an invoice becomes overdue, assuming a simple oversight.
2. **Firm reminder** — sent if payment still hasn't arrived after a reasonable follow-up window, referencing the specific overdue amount and due date.
3. **Escalation notice** — sent for significantly overdue or high-value balances, often paired with a hold on new orders until resolved.
4. **Account hold / manager escalation** — reserved for chronic non-payment or large exposure, where continuing to extend credit is no longer prudent without a business owner decision.

The tone and speed of escalation should scale with the customer's history — a first-time delay from a long-reliable customer warrants patience; a repeat pattern warrants a faster, firmer response.

## 4.7 Handling Late Payments

- A late payment is not automatically a crisis — context matters. A customer's history, the amount involved, and whether this is an isolated or repeated pattern should all shape the response.
- **Isolated, small, short delays** from otherwise reliable customers: routine reminder, no order restriction needed.
- **Repeated delays or growing overdue amounts**: warrants a firmer response and consideration of tightening credit terms going forward.
- **Large or long-overdue exposure**: warrants an order hold until resolved, and should be escalated for manager visibility rather than handled purely automatically.
- The AI should never let a growing overdue balance quietly continue accumulating further orders without surfacing it — silence here is a common source of bad debt.

## 4.8 Refund Policy

- Refunds should always be tied to a clear, verifiable reason (order error, damaged/incorrect goods, cancellation within policy) rather than processed automatically on request alone.
- Distinguish between a **refund** (money returned) and a **credit/adjustment** (applied against a future order) — the right choice depends on whether the customer intends to continue purchasing.
- Refund requests tied to a pattern (the same customer, repeated disputes) deserve a closer look — this may indicate a recurring fulfillment issue rather than isolated incidents, and should be flagged rather than processed silently each time.
- Large refunds should be flagged for manager awareness even when the underlying reason is valid, simply because of the cash flow and margin impact.

## 4.9 Customer Retention Tips

- Recognize and proactively support customers with consistent, growing order patterns — they are the business's most valuable relationships and merit responsive service.
- Address recurring complaints or fulfillment issues at the root cause, since repeated friction — even if each incident is individually minor — is what actually drives customers away.
- Use fair, proportionate credit and collections practices; overly aggressive handling of a minor, first-time delay can damage a relationship more than the overdue amount itself justifies.
- Flag customers whose order frequency is declining compared to their historical pattern — this is often an early, quiet warning sign worth investigating before the relationship is lost entirely.

## 4.10 AI Decision Guidelines

1. Always check credit exposure against the limit before recommending order approval — never assume approval by default.
2. Treat credit limit breaches as explicit exceptions requiring a flagged decision, not silent approvals.
3. Scale payment reminders and escalation to the customer's specific history, not a single fixed rule for everyone.
4. Distinguish an isolated late payment from a repeated or worsening pattern before recommending any account action.
5. Never let a growing overdue balance accumulate additional orders without surfacing it for review.
6. Tie refund recommendations to a clear reason, and flag recurring refund patterns for investigation.
7. Surface early signs of relationship change — rising credit utilization, declining order frequency — proactively.

## 4.11 Common Sales Mistakes

- Approving an order without checking current credit exposure against the limit.
- Applying the same collections urgency to a first-time minor delay and a chronic non-payer.
- Letting a customer's overdue balance grow silently while continuing to approve new orders.
- Processing refunds without verifying the underlying reason or noticing a repeated pattern.
- Treating all customers with a flat, one-size-fits-all credit policy regardless of history or value.
- Failing to notice a valuable customer's declining order frequency until the relationship is effectively lost.
- Reacting to late payments only after they become large, instead of catching early warning signs.

## 4.12 Manager Recommendations

- Review customer credit exposure regularly, not only at the moment of a new order.
- Set a clear, graduated reminder and escalation policy, and apply it consistently but proportionately.
- Reassess credit limits periodically based on updated payment history, not just at account opening.
- Investigate root causes behind repeated refund requests or complaints from the same customer.
- Balance firmness on chronic non-payment with flexibility for otherwise reliable, high-value relationships.

## 4.13 Business Scenarios

**Scenario 1 — Order Near Credit Limit**
A reliable, long-standing customer places an order that would bring their exposure just over their credit limit. *Correct reasoning:* flag the near-breach for a quick manager decision rather than silently approving or silently rejecting — context (their strong history) should inform, not override, the flag.

**Scenario 2 — First-Time Minor Delay**
A customer with a clean payment history is five days late on a small invoice for the first time. *Correct reasoning:* send a routine friendly reminder; no order hold or escalation warranted.

**Scenario 3 — Chronic Late Payer**
A customer has been late on the last four consecutive invoices, each time only after firm reminders. *Correct reasoning:* recommend tightening credit terms and consider an order hold until the current balance is resolved.

**Scenario 4 — Large Overdue Balance Growing**
A customer's overdue balance has been increasing over several weeks while new orders continue to be placed and approved. *Correct reasoning:* flag the pattern immediately and recommend a hold on new orders until the balance is addressed — this should not continue silently.

**Scenario 5 — Refund Request Pattern**
The same customer has requested refunds for "damaged goods" on three separate recent orders. *Correct reasoning:* flag the pattern for investigation — it may indicate a fulfillment or handling issue rather than approve each refund independently without noticing the trend.

**Scenario 6 — Declining Order Frequency**
A previously frequent, high-value customer's order frequency has dropped noticeably over recent months. *Correct reasoning:* flag this as an early retention concern worth proactive outreach, rather than waiting for the customer to stop ordering entirely.

**Scenario 7 — New Customer, Large First Order**
A newly onboarded customer with no payment history requests a large first order near a high credit limit. *Correct reasoning:* recommend a more conservative approach — a smaller initial limit or partial upfront payment — until a track record is established.

**Scenario 8 — Valuable Customer, Isolated Large Refund**
A high-value, reliable customer requests a legitimate, one-off large refund due to a genuine fulfillment error. *Correct reasoning:* approve the refund given the clear cause and customer history, but flag it for manager visibility due to its size.

## 4.14 Frequently Asked Questions

**Q1: Should every order be checked against the customer's credit limit?**
Yes — checking current exposure against the limit should happen before every order approval, without exception.

**Q2: What happens when an order would breach a customer's credit limit?**
It should be flagged as an explicit exception for a deliberate decision, never silently approved or silently rejected.

**Q3: Should all overdue payments trigger the same response?**
No — response should scale with the customer's history and the size/age of the overdue amount; a first-time minor delay differs meaningfully from a chronic pattern.

**Q4: How should the AI decide between a refund and a credit/adjustment?**
Based on whether the customer intends to continue purchasing — a refund returns cash, while a credit applies against future orders, which may better suit an ongoing relationship.

**Q5: Why does declining order frequency matter even if a customer hasn't complained?**
Because it's often a quiet early signal of a customer drifting away, and catching it early allows for proactive retention rather than reacting after the relationship is already lost.

**Q6: Should new customers get the same credit terms as established ones?**
No — new customers should start on a more conservative footing until a reliable payment history is established.

**Q7: What should trigger an account hold?**
Significant or chronic overdue exposure, or a clear repeated pattern of late payment — not an isolated, minor delay from an otherwise reliable customer.

**Q8: Why should repeated refund requests from the same customer be flagged?**
Because a pattern often points to a recurring fulfillment or quality issue that deserves investigation, rather than a series of unrelated incidents.

**Q9: Should collections be equally aggressive for all customers?**
No — collections should be proportionate; overly aggressive handling of a minor, first-time issue can damage a valuable relationship more than the overdue amount justifies.

**Q10: How does the sales workflow connect to inventory and cash flow?**
Every approved order reserves inventory and creates a receivable — so sales decisions directly affect stock availability and the cash position that funds future purchasing (see Chapter 1).
