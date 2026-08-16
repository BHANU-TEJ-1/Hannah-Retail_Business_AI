# Chapter 2: Product & Inventory Intelligence

## 2.1 Product Lifecycle

Every product moves through a lifecycle, and the right business action depends on knowing which stage a product is in:

- **Introduction** — Newly added to the catalog. Demand is unproven. Stock should be conservative, sourced in smaller batches, and closely watched for early sell-through signals.
- **Growth** — Demand is rising and repeat orders are appearing. This is when reorder quantities should scale up and a reliable primary supplier should be locked in.
- **Maturity** — Demand is stable and predictable. This is the ideal state for standard reorder-point logic to run with minimal manual intervention.
- **Decline** — Sales are slowing, often due to a newer alternative, seasonality ending, or changing customer preference. Reorder quantities should shrink, and existing stock should be sold down rather than replenished.
- **Discontinuation** — The product is being phased out. No further purchase orders should be placed; remaining stock should be cleared, potentially at a discount, to recover cash.

The AI should always reason about *where a product sits in this lifecycle* before recommending a reorder — a slowdown in a mature product is a red flag, but the same slowdown in a declining product is expected and not a problem to fix.

## 2.2 Product Categories

Products are typically grouped by **category** and **brand**, and grouping matters because retail decisions are rarely made one SKU at a time:

- **Category-level view** helps identify whether a whole category is trending up or down (useful for supplier negotiation and shelf/warehouse space planning).
- **Brand-level view** helps identify supplier concentration risk — if one brand dominates sales but has only one supplier, that's a fragility worth flagging.
- **Unit-level consistency** (how a product is measured and sold — pieces, boxes, kilograms, etc.) must stay consistent across purchasing and selling, since a mismatch here is a common source of stock discrepancies.

## 2.3 Fast vs. Slow-Moving Products

- **Fast-moving products** sell frequently and predictably. They deserve tighter reorder monitoring, higher reorder priority, and are the most sensitive to stockouts — a stockout on a fast-mover costs real, immediate revenue.
- **Slow-moving products** sell infrequently. They deserve smaller, less frequent purchase orders and closer scrutiny before every reorder — the risk here isn't stockout, it's tying up cash and warehouse space in stock that won't turn over.
- **Dead stock** is the extreme end of slow-moving: stock that hasn't sold in a long period relative to its category norm. This should be actively flagged for clearance, discounting, or write-off consideration — it is quietly costing the business money simply by existing.

A simple rule of thumb: **the faster a product moves, the more urgently the AI should react to low stock; the slower it moves, the more urgently the AI should react to excess stock.**

## 2.4 Inventory Concepts

The AI must consistently distinguish between:

- **On-hand quantity** — physically present in a warehouse right now.
- **Reserved quantity** — already committed to open customer orders, not free to sell again.
- **Available quantity** — on-hand minus reserved; the true sellable figure.
- **Incoming quantity** — on order from a supplier but not yet received.
- **Total position** — available plus incoming; the fullest picture of what will be sellable soon.

Every inventory judgment — reorder, stockout risk, overstock — should be based on **available quantity** and **total position**, never on-hand alone. On-hand alone is the single most common cause of bad recommendations.

## 2.5 Reorder Strategy

A disciplined reorder strategy balances three questions: **when to reorder, how much to reorder, and from whom.**

- **When**: Reorder when available quantity approaches the product's reorder level — the threshold set to cover expected demand during the supplier's typical lead time, plus a buffer (safety stock).
- **How much**: Order the product's defined reorder quantity as a baseline, but adjust up for products in a growth phase or upcoming seasonal demand, and adjust down for products in decline.
- **From whom**: Default to the product's designated primary supplier unless that supplier currently has performance, pricing, or delivery issues serious enough to justify a switch (see Chapter 3 for supplier evaluation logic).

Reorder decisions should also account for **incoming stock already on order** — recommending a second purchase order when one is already in transit for the same product is a common and costly mistake.

## 2.6 Safety Stock

Safety stock is the buffer held above expected demand to absorb uncertainty — in customer demand, in supplier delivery timing, or both. It is not wasted stock; it is insurance.

- Products with **longer or less reliable supplier lead times** need more safety stock.
- Products with **volatile or seasonal demand** need more safety stock.
- Products that are **fast-moving and business-critical** (best sellers, or products tied to key customer relationships) warrant a higher safety stock buffer even if this ties up more cash — the cost of a stockout on these products outweighs the carrying cost.
- Products that are **slow-moving or low-value** should carry minimal to no safety stock — the carrying cost isn't justified by the risk.

## 2.7 Overstock vs. Understock

Both are business risks, but they cost the business in different ways:

| | Understock | Overstock |
|---|---|---|
| **Immediate cost** | Lost sales, disappointed customers | Tied-up cash |
| **Ongoing cost** | Damaged customer trust, urgent/expensive reorders | Storage cost, risk of obsolescence or spoilage |
| **Typical cause** | Ignoring reserved stock, underestimating demand, supplier delay | Over-ordering "just in case," ignoring slowing sales trend |
| **AI response** | Recommend urgent reorder or transfer | Recommend sell-down, discount, or halt future orders |

The AI should never treat "more stock" as inherently safer — overstock is a real and costly business risk, not a neutral outcome.

## 2.8 Inventory Movement Concepts

Stock changes for identifiable reasons, and the AI should reason about *why* stock moved, not just *that* it moved:

- **Sale/fulfillment** — stock decreases as customer orders are delivered.
- **Purchase receipt** — stock increases as supplier deliveries are received.
- **Warehouse transfer** — stock moves between warehouses without a net change to the business's total position.
- **Adjustment/correction** — stock changes due to damage, loss, miscount, or correction — this category deserves manager attention, since frequent adjustments usually signal a process problem worth investigating, not just a number to accept.

A sudden or repeated inventory adjustment on the same product is a signal worth flagging — it often points to a real operational issue (theft, damage, mis-picking) rather than a one-off event.

## 2.9 Inventory Decision Guidelines

1. Always evaluate reorder need using **available quantity**, adjusted for **incoming quantity** already on order.
2. Weight reorder urgency by **how fast the product moves** — fast movers get faster action.
3. Consider the product's **lifecycle stage** before recommending a reorder quantity — never recommend growth-phase quantities for a declining product.
4. When stock is uneven across warehouses, **prefer a transfer over a new purchase** if it solves the shortfall.
5. Flag **excess/dead stock** proactively — don't wait for a manager to ask.
6. Treat repeated **inventory adjustments** on the same product as an operational red flag, not routine noise.
7. Factor in **upcoming seasonal demand** before it hits, not after stock has already run out.

## 2.10 Storage Best Practices

- Keep fast-moving products in the warehouse(s) closest to the largest concentration of customer demand, minimizing fulfillment delays.
- Avoid concentrating all stock of a critical product in a single warehouse — distribute enough to cover regional demand and reduce the impact of a single-location disruption.
- Regularly reconcile expected stock against actual counts; unexplained gaps should trigger investigation, not just an adjustment entry.
- Keep slow-moving and seasonal-off stock in lower-priority storage, freeing prime space for active, fast-moving inventory.

## 2.11 Seasonal Inventory Planning

- Identify products with a clear seasonal sales pattern and increase reorder quantities **ahead of** the season, factoring in supplier lead time so stock arrives before demand peaks — not during or after.
- After a seasonal peak ends, reduce or halt reordering promptly to avoid carrying leftover seasonal stock at low season into the next cycle.
- Use the prior year's seasonal pattern (where available) as a guide, but adjust for known changes — a new customer contract, a discontinued competitor, or a shifted trend.
- Treat seasonal safety stock differently from year-round safety stock — it should be tied to a defined window, not held indefinitely once the season passes.

## 2.12 Common Mistakes

- Using on-hand quantity instead of available quantity when judging whether to reorder.
- Reordering a product that already has a large incoming purchase order in transit.
- Applying the same reorder urgency to fast- and slow-moving products alike.
- Letting a declining product continue to be reordered at growth-phase quantities out of habit.
- Ignoring uneven stock distribution across warehouses and defaulting to a new purchase instead of a transfer.
- Failing to flag dead stock until it has sat unsold for a very long time, by which point recovery options are limited.
- Reacting to seasonal demand only after a stockout has already occurred.
- Treating frequent inventory adjustments as routine data noise rather than an operational signal.

## 2.13 Manager Recommendations

- Review fast-moving products at least weekly; slow-moving products can be reviewed monthly.
- Build seasonal reorder timing backward from the season's start date, using supplier lead time as the anchor.
- Set a dead-stock threshold (e.g., no sales in a defined period relative to the category norm) and review that list regularly, not opportunistically.
- When in doubt between reordering and transferring, always check other warehouses first — transfers are faster and cheaper than new purchases.
- Treat safety stock as a deliberate, product-specific decision, not a flat percentage applied to everything.

## 2.14 Business Scenarios

**Scenario 1 — Reorder Despite Incoming Stock**
A product's available stock is below its reorder level, but a purchase order for the same product is already incoming and will arrive well before stock runs out. *Correct reasoning:* no new order needed; the total position (available + incoming) already covers demand.

**Scenario 2 — Fast-Mover Near Reorder Point**
A best-selling product's available stock drops close to its reorder level heading into a normal week. *Correct reasoning:* reorder promptly — fast movers carry high stockout cost and little tolerance for delay.

**Scenario 3 — Slow-Mover With Moderate Stock**
A slow-moving product still has several months of stock at its current sales pace. *Correct reasoning:* do not reorder yet, even if technically near a generic threshold — recommend monitoring instead.

**Scenario 4 — Declining Product, Habitual Reorder Requested**
A manager requests the usual reorder quantity for a product now in clear decline. *Correct reasoning:* recommend a reduced quantity or pause, and flag the declining trend rather than auto-approving the habitual amount.

**Scenario 5 — Uneven Warehouse Stock**
One warehouse is critically low on a product while another warehouse holds excess of the same product. *Correct reasoning:* recommend an inter-warehouse transfer before recommending a new supplier purchase.

**Scenario 6 — Pre-Season Planning**
A product has a known seasonal spike two months away, and current stock reflects off-season levels. *Correct reasoning:* recommend increasing the next purchase order now, timed to arrive before the season begins, factoring in supplier lead time.

**Scenario 7 — Repeated Stock Adjustments**
A product has had several unexplained inventory adjustments in recent weeks. *Correct reasoning:* flag this as an operational concern requiring investigation, not just log the adjustments.

**Scenario 8 — Dead Stock Discovery**
A product has not sold in a period far exceeding its category's normal turnover. *Correct reasoning:* recommend clearance or discounting to recover cash and free storage, and halt any further reordering.

## 2.15 Frequently Asked Questions

**Q1: What's the difference between on-hand and available stock?**
On-hand is everything physically present; available is on-hand minus stock already reserved for open customer orders. Decisions should use available stock.

**Q2: Why shouldn't every product carry the same safety stock buffer?**
Because risk differs by product — fast movers and long-lead-time products need more buffer, while slow movers and low-value products don't justify the extra carrying cost.

**Q3: Is more inventory always safer than less?**
No. Overstock ties up cash and risks obsolescence — it's a real cost, not a neutral safety margin.

**Q4: How should the AI treat a product already in decline?**
Recommend smaller or paused reorders and encourage selling down existing stock rather than replenishing at prior levels.

**Q5: When should a transfer be recommended instead of a new purchase order?**
Whenever another warehouse holds excess of the same product that could reasonably reach the location in need — transfers are typically faster and cheaper than new procurement.

**Q6: How far ahead should seasonal reordering begin?**
Early enough that, accounting for the supplier's typical lead time, stock arrives before the seasonal demand starts — not after it has already begun.

**Q7: What counts as dead stock?**
Stock that has gone unsold for significantly longer than what's normal for its category, indicating it's unlikely to sell through at a normal pace.

**Q8: Why are repeated inventory adjustments a concern?**
Because they often indicate an underlying operational issue — damage, mis-picking, theft, or process errors — rather than random, one-off events.

**Q9: Should reorder quantity always match the product's default reorder quantity?**
Not automatically — it should be adjusted for lifecycle stage, upcoming seasonality, and current sales trend, using the default as a baseline, not a fixed rule.

**Q10: How should incoming stock affect a reorder decision?**
It should always be factored in — recommending a new order without checking for incoming stock already in transit risks creating unnecessary overstock.
