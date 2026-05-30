# The Free Rider Problem

## What economists already know

In 1968, Garrett Hardin published "The Tragedy of the Commons" — the observation that shared resources, when accessible to all, tend to be overexploited by individuals acting in self-interest until the resource is depleted for everyone. He was writing about grazing land. The same logic applies to AI subscription free tiers, almost without modification.

A free rider is someone who consumes a shared resource without contributing to its cost. The resource here is AI inference capacity: the compute that runs Claude, ChatGPT, or any other frontier model. Each query costs real money — fractions of a cent for short completions, dollars for long multi-turn sessions with tool use. When someone creates a second account to reset their usage quota, they are free-riding on infrastructure paid for by subscribers who convert.

The free rider problem is hard to solve not because free riders are hard to find, but because the incentive structure makes free-riding *rational*. If the cost of creating a new account is near zero (an email address, two minutes of time) and the benefit is continued access to a $20/month product, the math is obvious. Blaming users for doing this is like blaming water for flowing downhill.

## Why companies let it happen

Rational product managers at AI companies make a calculated tradeoff: be generous with free tiers to drive adoption, accept some abuse, and optimize conversion rates for users who stay. The thinking is that aggressive anti-abuse measures impose friction that hurts legitimate users more than it deters sophisticated abusers.

This is correct, as far as it goes. But it collapses at scale. At 100 million users, even a 2% abuse rate represents 2 million accounts consuming capacity without revenue. The commons tips.

## The collective action problem

Individual free riders don't think of themselves as destroying a shared resource. They think: "I'm just one person. My second account doesn't matter." They are correct — individually. But the aggregate effect of millions of individually-harmless decisions is a material cost burden on the company.

This is textbook collective action failure. The solution economists reach for is either exclusion (deny access to non-contributors) or regulation (make free-riding costly enough to deter). For AI companies, exclusion is the detection problem this framework addresses.

## Why this isn't a moral argument

This document is not arguing that multi-account users are bad people. Many of them are developers, researchers, or cost-conscious individuals who are doing nothing that violates their intuitive sense of fairness. The free rider problem is structural, not moral.

Understanding it as structural matters for detection design: the right framing isn't "how do we catch cheaters" but "how do we accurately measure the scope of behavior that is economically unsustainable, and respond proportionally." That framing leads to very different system designs.

---

*Next: [Why AI products are uniquely vulnerable](why_ai_products_are_uniquely_vulnerable.md)*
