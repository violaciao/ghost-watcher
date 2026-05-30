# Metrics Taxonomy

Not all signals are created equal. Some things you can observe directly. Some things you infer from behavioral proxies. Some things you can only estimate statistically. Conflating these tiers is how abuse measurement goes wrong.

This taxonomy organizes metrics by observability — how much epistemic distance sits between the raw data and the conclusion you're drawing.

---

## Layer 1: Directly Observable

These metrics require no inference. They are facts about system events that you either recorded or didn't.

| Metric | Definition | Notes |
|--------|-----------|-------|
| `accounts_per_ip` | Number of distinct accounts ever associated with an IP address | VPNs inflate this; use rolling windows |
| `accounts_per_device_fingerprint` | Accounts sharing the same (OS, browser, screen_res, UA) composite | Fingerprint collisions exist — not 1:1 with physical device |
| `email_domain_type` | Disposable / free webmail / corporate / custom | Disposable email lists need regular refreshing |
| `account_age_at_quota_exhaust` | Days between account creation and first quota exhaustion | -1 if never exhausted |
| `registration_velocity_from_ip` | Accounts created from same IP in rolling 7-day window | Primary signal for coordinated creation |
| `ip_asn_type` | Residential / datacenter / VPN / Tor exit node | Datacenter + high usage is a strong signal |
| `email_creation_timestamp_delta` | Time between this account's email registration and product signup | Near-zero delta = disposable email created for signup |

**Interpretation caution:** observable facts can still be misleading. An IP address is not a person. A shared IP from a university or corporate VPN will show many accounts per IP that are entirely legitimate.

---

## Layer 2: Behavioral Proxies

These metrics require aggregation and pattern matching across events. They are observed but not direct — they require a model of what "normal" looks like to be interpretable.

| Metric | Definition | Normal range | Abuse signal |
|--------|-----------|--------------|-------------|
| `quota_exhaustion_speed_hrs` | Time from account activation to first quota hit | 15–45 days | < 48 hours |
| `session_depth_ratio` | Avg messages per session / median for plan tier | 0.7–1.3 | > 3.0 (power usage) or < 0.2 (probe & leave) |
| `return_rate_7d` | % of accounts returning after day 1 | 35–65% | < 5% (one-time extraction) |
| `api_calls_per_session` | Mean API calls per active session | Varies by plan | Extreme outliers |
| `feature_breadth_score` | Number of distinct product features used | Higher = more engaged | Very low = narrow extraction |
| `days_between_accounts` | For linked account clusters: gap between creations | N/A | < 3 days suggests cycling |
| `conversion_rate_by_cohort` | % converting to paid, by acquisition source and behavior cluster | 3–8% | < 0.5% in high-usage cohorts |

**Interpretation caution:** behavioral proxies encode assumptions about what legitimate users do. Those assumptions can be wrong, biased toward the behavior of reviewers rather than the actual user distribution, and can shift over time as product features change.

---

## Layer 3: Estimated

These are quantities you cannot directly measure. They require statistical inference, often from multiple noisy inputs. Report them with confidence intervals, always.

| Metric | Estimation approach | Key assumption | Uncertainty source |
|--------|--------------------|-----------------|--------------------|
| `true_abuse_rate` | Stratified sampling + human review on random sample | Reviewer accuracy > 80% | Reviewer disagreement, selection bias |
| `accounts_per_abuser` | Cluster analysis on linked accounts / estimated unique abusers | Clustering correctly identifies co-ownership | Shared devices, VPNs creating false links |
| `revenue_lost_per_month` | `abuse_rate × MAU × ARPU_paid × conversion_rate_counterfactual` | What abusers *would* pay without free tier access | Conversion rate assumption is highly uncertain |
| `detection_recall` | Estimated from labeled holdout + adjustment for label noise | Label noise is randomly distributed (it isn't) | Systematic labeling errors |
| `incremental_conversion_from_enforcement` | A/B test on enforcement intensity vs conversion outcome | Clean accounts not affected by false positive friction | Spillover effects |

**The cardinal rule for Layer 3:** never report a point estimate without a range. "We estimate 2.3% of accounts are abusive" is a statement that implies more precision than the data supports. "We estimate 1.5–4.1% at 90% confidence" is honest.

---

## Metric Interaction Effects

Metrics from different layers interact in ways that can compound errors:

- Using Layer 1 signals as training labels for a model that predicts Layer 3 estimates creates circular reasoning
- Optimizing a detection system against Layer 2 proxies improves proxy precision without necessarily improving true abuse detection
- Layer 3 estimates often use Layer 2 proxies as inputs, so uncertainty at Layer 2 propagates upward

The framework in this project keeps these layers separate throughout: Layer 1 feeds into rule-based heuristics, Layer 2 drives behavioral feature engineering for ML, and Layer 3 is estimated from held-out audit samples with explicit uncertainty bounds.

---

*Next: [Abuse confidence score](abuse_confidence_score.md)*
