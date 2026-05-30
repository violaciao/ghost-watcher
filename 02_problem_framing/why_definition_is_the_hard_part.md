# Why Definition Is the Hard Part

The standard narrative around abuse detection goes like this: collect data, label it, train a model, ship it, iterate. The hard part is the model. With enough data and the right features, the classifier will figure out the rest.

This narrative is wrong for subscription abuse. The hard part is the labeling step, and no amount of modeling sophistication fixes a broken label.

## The Core Problem: Ground Truth Scarcity

To train a supervised classifier, you need labeled examples of abuse and non-abuse. Where do those labels come from?

**Option 1: Human review.** Have a Trust & Safety team investigate flagged accounts and make determinations. This is slow, expensive, and introduces observer bias (reviewers develop intuitions that may or may not reflect reality). At scale, human review is a bottleneck that can only cover a tiny fraction of suspicious accounts.

**Option 2: Proxy signals.** Use hard signals as labels — IP overlap, disposable email domain, same device fingerprint across accounts. But these signals are exactly what you're trying to predict. Using them as labels instead of features creates a model that learns to detect your own heuristics, not actual abuse.

**Option 3: User self-report or confession.** Essentially nonexistent. Abusers do not fill out the "I have 6 accounts" survey.

**Option 4: Downstream outcomes.** Label accounts that never converted and had specific behavioral patterns as "likely abuse." But a user who didn't convert isn't necessarily an abuser — they may have tried the product and decided it wasn't worth $20/month. Conflating non-conversion with abuse is one of the most common errors in Trust & Safety data science.

None of these options provide clean ground truth. Each introduces systematic error in a different direction.

## Observer Bias

The people who build abuse detection systems are, almost by definition, not the people who abuse subscriptions. They tend to have different intuitions about what "normal" behavior looks like.

Consider session patterns. A Trust & Safety reviewer who sees an account that exhausted its quota in 4 hours may flag it as suspicious — that's not how *they* use the product. But a developer stress-testing an integration might exhaust quota in 4 hours routinely, legitimately, and non-abusively.

Observer bias in labeling produces training data that systematically over-represents the reviewer's model of normal behavior. The classifier then learns that model, not the actual distribution of user behavior. This is a subtle form of garbage-in-garbage-out that can persist undetected for a long time because the model *looks* like it's working — it agrees with the reviewers who labeled it.

## The Proxy Label Tradeoff

The most common practical approach is to use a combination of hard signals as a proxy for the abuse label. A typical rule might be:

> `is_abuse = 1` if: (same IP as 2+ other accounts) AND (email is disposable domain) AND (quota exhausted within 48h)

This is not unreasonable. But it has structural consequences:

1. **It defines abuse by signal, not behavior.** An account that shares all three signals but belongs to a legitimate user gets labeled as abuse. An account that is genuinely abusive but evades all three signals gets labeled clean.

2. **It creates a ceiling on model performance.** Your trained model cannot outperform the proxy labels it was trained on. If your labels are 85% accurate (a generous estimate), your model's precision is bounded at roughly that level.

3. **It measures your detection capability, not the true abuse rate.** This distinction matters enormously for business impact reporting. If you say "our model catches X% of abuse accounts," you should be reporting X% of the accounts that match your proxy labels, not X% of actual abuse — and those are different things.

## Binary Labels Are Epistemically Dishonest

The standard ML practice of using a binary `is_abuse` label (0 or 1) encodes a level of certainty that the evidence cannot support.

When a reviewer looks at an account and calls it "abuse," they are making a probabilistic judgment with meaningful uncertainty. Encoding that as `1` and treating it as ground truth propagates that uncertainty invisibly into every downstream model, metric, and business decision. The false precision is worse than no label at all, because it looks rigorous.

The alternative — which this framework adopts throughout — is a three-tier confidence system:

- `high_confidence_abuse`: multiple independent hard signals co-occurring; probability of error is low
- `suspected`: one or more soft signals, inconclusive; requires further investigation or policy decision
- `clean`: no significant signals detected; absent evidence of abuse

This is not a concession to imprecision. It is an accurate representation of the epistemic state. Models trained against this label distribution can expose their own uncertainty rather than hiding it in a confident-looking probability score.

## What Good Measurement Looks Like

Given these constraints, a rigorous abuse measurement framework should:

1. **Distinguish between abuse rate estimation and abuse detection.** Estimating the *prevalence* of abuse is a statistical problem (capture-recapture, stratified sampling). Detecting *specific* abuse accounts is a classification problem. Conflating them produces wrong answers to both questions.

2. **Report uncertainty explicitly.** A point estimate of "2.3% of accounts are abusive" is almost certainly wrong. A confidence interval of "1.5%–4.1% at 90% confidence" is honest.

3. **Separate signal from label.** Never use detection signals as training labels for a model that uses those same signals as features. This isn't just methodologically wrong — it's circular.

4. **Treat non-conversion as a distinct outcome.** A user who doesn't convert is a conversion problem, not necessarily an abuse problem. These require different interventions.

5. **Revisit labels as policy changes.** What counts as abuse today may not count tomorrow (and vice versa). Labels need to be tied to a specific policy version.

The goal of this framework is not to pretend these problems are solved. It's to build analytical infrastructure that keeps them visible.

---

*Next: [Metrics taxonomy](../03_metrics/taxonomy.md)*
