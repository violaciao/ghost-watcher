# Abuse Confidence Score

## The Problem with Binary Labels

Most ML pipelines for abuse detection use a binary label: `is_abuse = 0` or `is_abuse = 1`. This is a choice that looks natural because classifiers are often framed as binary problems, but it's wrong for this domain for a specific reason:

**The evidence for abuse is rarely conclusive.** An account that shares an IP with two others and exhausted quota in 36 hours might be an abuser, or it might be a developer working from a shared office on a time-sensitive project. Encoding that ambiguous evidence as `is_abuse = 1` is an epistemically dishonest choice that propagates false confidence through every downstream system.

The alternative used throughout this project is a three-tier confidence label system.

---

## The Three Tiers

### `high_confidence_abuse`

**Definition:** Multiple independent hard signals co-occurring, with no plausible legitimate explanation.

**Signal threshold:** At least 3 of the following, including at least 1 starred (*):
- (*) Disposable or newly-created email domain
- (*) Same exact device fingerprint as 2+ other accounts in rolling 90-day window
- (*) Quota exhausted within 48 hours of account creation
- Same ASN as known VPN or datacenter, combined with high usage
- Account registration within 3 days of another linked account
- Zero meaningful activity after quota exhaustion (never returns)
- IP appears in 5+ accounts within a 7-day window

**Expected precision:** > 90% (estimated; unverifiable without ground truth)

**Business action:** Eligible for automated enforcement — account suspension, block on new account creation from linked identifiers.

---

### `suspected`

**Definition:** One or more soft signals present, but evidence is inconclusive. Requires human review or policy decision before enforcement.

**Signal threshold:** 1–2 signals from the high_confidence list, OR behavioral patterns that are statistically anomalous but have plausible legitimate explanations.

Examples:
- IP overlap with 2 other accounts, but from a university ASN
- Quota exhausted in 72 hours, but user has returned and shows deep session engagement
- Disposable email domain, but account has converted to paid
- Behavioral fingerprint matches another account, but accounts have different countries

**Expected precision:** 50–75% (wide range because this tier absorbs genuine ambiguity)

**Business action:** Flag for review. Do not automate enforcement. May qualify for "soft friction" interventions (phone verification request, payment method requirement) pending policy decisions.

---

### `clean`

**Definition:** No significant signals detected. Absence of evidence is not evidence of absence, but no action is warranted.

**Signal threshold:** Zero signals from the detection rule set, or signals that have been investigated and explained.

**Expected recall:** High false negative rate is expected and acceptable at this confidence level. The `clean` label means "we have no basis to act," not "we are confident this is not abuse."

**Business action:** None. Standard user experience.

---

## Why Not a Continuous Score?

A model probability (e.g., `abuse_score = 0.73`) might seem more informative than a three-tier label. It has two problems:

1. **False precision.** A score of `0.73` implies the model knows the difference between 0.71 and 0.75. Given the label noise in training data, it almost certainly does not. The precision of the score exceeds the precision of the underlying evidence.

2. **Threshold arbitrariness.** Any continuous score requires a threshold for action. That threshold is a policy decision that shouldn't be hidden inside a model. Making the tiers explicit forces the policy decision into the open, where it can be debated and documented.

The three-tier system does not preclude using continuous scores internally. A model can output `P(high_confidence_abuse)` and `P(suspected)`, which are then mapped to tiers using policy-defined thresholds. The point is that the *label* exposed to downstream systems and humans should be a tier, not a probability.

---

## Label Versioning

Abuse policy changes. What qualifies as `high_confidence_abuse` today may not qualify tomorrow (threshold changes, new signal added, new legitimate use case discovered). Labels must be versioned.

Each labeled record in this dataset includes:
- `abuse_confidence`: the tier (`high_confidence_abuse`, `suspected`, `clean`)
- `abuse_signals`: list of specific signals that triggered the label
- `label_version`: the policy version under which the label was assigned
- `label_source`: `rule` (automated) or `human_review`

This allows retrospective analysis: if policy changes, old labels can be reprocessed and the effect on estimated abuse rates can be measured.

---

*Next: [RBA dataset overview](../04_data/rba_dataset_overview.md)*
