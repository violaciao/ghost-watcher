# What Is Subscription Abuse?

Before building any detection system, you need a precise definition of what you're detecting. This document defines the scope of this project explicitly, including what is explicitly *out* of scope.

## In Scope: Multi-Account Abuse

This project focuses on one specific behavior: **a single real-world individual controlling multiple accounts in order to obtain more free-tier usage than the product intends to provide.**

The key elements:
- **Single real-world individual**: one human, not one device or one IP
- **Multiple accounts**: two or more accounts across any combination of email addresses
- **Intent to exceed free tier**: the motivation is usage, not legitimate product testing or access management

This is sometimes called "ghost account" abuse, "free tier stacking," or "trial cycling." The accounts themselves may be technically legitimate — valid email addresses, real sign-up flows — but their collective use represents an extraction of value the business did not intend to provide for free.

## Out of Scope

The following are related but distinct problems that this framework does not address:

**Payment fraud**: using stolen credit cards to create paid accounts. Different signal space, different detection approach, handled by fraud teams and payment processors (Stripe Radar, etc.).

**Credential stuffing**: using leaked credentials to take over existing accounts. An authentication security problem, not a subscription abuse problem.

**Account sharing**: one account used by multiple real people (e.g., a family sharing a subscription). This is a separate policy question and a separate detection problem. The signals overlap with multi-account abuse but the economic impact and the appropriate response differ significantly.

**Bot traffic / automated abuse**: non-human agents making bulk API requests. Related to multi-account abuse but typically addressed at the API rate-limiting layer.

**Prompt injection / jailbreaking**: attempts to circumvent safety filters. A content moderation problem, not a Trust & Safety measurement problem.

## Why This Scoping Decision?

Multi-account abuse is the most measurement-tractable of these problems because it leaves device and behavioral fingerprints across accounts. It is also the most directly tied to revenue leakage in the free tier → paid tier conversion funnel, which makes it a clear business priority.

The other problems listed above either have established solutions in adjacent domains (payment fraud), don't primarily affect the free tier economics (account sharing), or require fundamentally different detection architectures (bot traffic, content abuse).

Scoping tightly also forces discipline in the labeling process. A definition that includes "any behavior we don't like" produces garbage labels. A definition that specifies "one human, multiple accounts, intent to exceed free tier" is at least arguable.

## The Awkward Edge Cases

Even this narrow definition runs into hard cases:

- A developer creates a second account under their company name to test integration behavior. Abuse? No. But the signals look identical to abuse.
- A privacy-conscious user creates a fresh account every few months to limit tracking. Abuse? Arguably not. Signals: indistinguishable from cycling.
- A household of two people shares a computer with separate accounts. Abuse? No. Signal: IP overlap.
- A user who intended to abuse creates an account, uses it legitimately for a month, then converts to paid. Abuse? The intent was there; the outcome was fine.

These edge cases are not corner cases. They are frequent enough that any detection system that treats them as noise will have unacceptable false positive rates.

This is the entry point to the core thesis of this project, explored in full in the next document.

---

*Next: [Why definition is the hard part](why_definition_is_the_hard_part.md)*
