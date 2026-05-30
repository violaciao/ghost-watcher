# Why AI Products Are Uniquely Vulnerable

Subscription abuse is not new. People have been sharing Netflix passwords and stacking Spotify free trials for years. But AI products face a specific combination of factors that makes them disproportionately attractive to abuse — factors that don't all apply to streaming or SaaS.

## Factor 1: Extremely high perceived value, low friction to switch

A ChatGPT Plus subscription at $20/month gives users access to GPT-4, which can write code, draft contracts, summarize research, and do work that would otherwise cost hundreds of dollars of human time. The perceived value-to-price ratio is unusually high.

When the value gap between free and paid is that large, the incentive to game the free tier is correspondingly large. Compare this to a password manager at $3/month, where the premium features are marginal enough that most users just pay.

## Factor 2: Near-zero marginal cost *per account*

Creating a new account at OpenAI, Anthropic, or GPTZero requires: an email address. That's it. No phone number verification in most flows. No credit card. No identity check. The cost of creating a second (or sixth) account is approximately zero for users who know what they're doing.

This is partly by design — high-friction onboarding kills growth. But it means the barrier to abuse is artificially low.

## Factor 3: Generous free tiers that reset on a schedule

"Free, then pay when you hit the limit" is the standard AI product growth model. It works great for converting trial users. It also creates a predictable exploitation pattern: exhaust the free tier, create a new account, repeat.

OpenAI has rotated through multiple free tier structures — a fixed number of GPT-4 queries per month, time-limited access, usage-based caps — each of which was gamed shortly after launch. The reset cadence creates a natural abuse rhythm.

## Factor 4: High compute cost per user

Unlike streaming, where the marginal cost of serving one more user is near-zero (bandwidth is cheap at scale), AI inference is expensive. Running a frontier model costs real money per query. A user who burns through their free tier in two days and creates a new account is imposing real infrastructure cost, not just accounting cost.

This is why the business impact of ghost accounts at AI companies is materially different from password sharing at Netflix. It's not just lost subscription revenue — it's also direct cost of goods.

## Factor 5: The developer/power user segment blurs the line

AI products attract a disproportionate share of technically sophisticated users: developers, researchers, prompt engineers, people who know exactly how the systems work. This population is both more likely to create workaround accounts *and* more likely to have legitimate reasons for doing so (testing, evaluation, separate contexts).

This creates a detection nightmare. The behavioral signature of a developer testing API behavior across two accounts looks identical to an abuser cycling through free tiers. The companies most affected — Anthropic, OpenAI — have massive developer communities, which means a huge proportion of their "suspicious" accounts may be completely legitimate.

## What this means for detection

GPTZero has publicly described dealing with students creating multiple accounts to circumvent detection limits. OpenAI has rotated free tier structures repeatedly in response to documented gaming behavior. Anthropic faces the same dynamics with Claude.

None of these companies have published a public measurement of their abuse rates, for obvious reasons. But the structural conditions make it nearly certain that multi-account abuse is a material cost driver at each of them.

The combination of high value, low account friction, generous free tiers, and high compute costs creates an unusually favorable environment for free riding. That's the baseline any detection framework has to contend with.

---

*Next: [What is subscription abuse?](../02_problem_framing/what_is_subscription_abuse.md)*
