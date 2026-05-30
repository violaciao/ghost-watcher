# Schema Design

The simulated dataset combines three layers: device fingerprint (sourced from the RBA dataset), account-level attributes, and behavioral signals. A label layer is computed from the combination of these signals.

## Full Schema

### Device Fingerprint Layer
*(sampled from RBA dataset)*

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `ip_address` | string | IPv4 address at account creation | `192.168.1.42` |
| `country` | string | ISO 3166-1 alpha-2 country code | `US` |
| `asn` | string | Autonomous System Number | `AS7922` |
| `asn_org` | string | ASN organization name | `Comcast Cable` |
| `asn_type` | string | `residential` / `datacenter` / `vpn` / `tor` | `residential` |
| `os_name` | string | Operating system | `Windows 10` |
| `browser_name` | string | Browser name | `Chrome` |
| `device_type` | string | `Desktop` / `Mobile` / `Tablet` | `Desktop` |
| `user_agent` | string | Full UA string | `Mozilla/5.0 (Windows NT 10.0...)` |
| `round_trip_time_ms` | float | Network RTT in milliseconds | `34.2` |

### Account Layer

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `account_id` | string | UUID v4 | `a3f7c2d1-...` |
| `account_created_at` | datetime | Account creation timestamp | `2025-03-14 09:22:11` |
| `email_address` | string | Account email | `user@gmail.com` |
| `email_domain` | string | Email domain | `gmail.com` |
| `email_domain_type` | string | `disposable` / `free_webmail` / `corporate` / `custom` | `free_webmail` |
| `plan_type` | string | `free` / `trial` / `paid_monthly` / `paid_annual` | `free` |
| `is_converted` | bool | Whether account ever reached paid status | `False` |
| `conversion_date` | datetime | Date of first conversion (null if never) | `null` |
| `linked_account_cluster` | string | Cluster ID for accounts sharing device fingerprint | `cluster_0042` |
| `accounts_in_cluster` | int | Number of accounts in this cluster | `3` |

### Behavior Layer

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `days_active` | int | Total days with at least one session | `4` |
| `total_sessions` | int | Lifetime session count | `12` |
| `avg_session_duration_mins` | float | Mean session duration in minutes | `8.3` |
| `api_calls_count` | int | Total API calls / model queries | `847` |
| `features_used` | int | Count of distinct product features touched | `2` |
| `quota_exhausted` | bool | Whether quota was ever exhausted | `True` |
| `quota_exhausted_at` | datetime | Timestamp of first quota exhaustion (null if never) | `2025-03-16 14:05:33` |
| `hours_to_quota_exhaustion` | float | Hours from account creation to quota hit (null if never exhausted) | `52.7` |
| `return_after_exhaustion` | bool | Whether account had activity after quota exhaustion | `False` |
| `days_since_last_active` | int | Days between last activity and observation date | `45` |

### Label Layer

| Column | Type | Description | Values |
|--------|------|-------------|--------|
| `abuse_confidence` | string | Three-tier abuse label | `high_confidence_abuse` / `suspected` / `clean` |
| `abuse_signals` | string | Pipe-delimited list of triggered signals | `disposable_email\|ip_cluster\|fast_exhaust` |
| `label_version` | string | Policy version for label | `v1.0` |
| `label_source` | string | How label was assigned | `rule` / `human_review` |

---

## Key Design Decisions

**Why `linked_account_cluster` instead of a foreign key?** The cluster captures the abuse pattern at the schema level — accounts that share fingerprints are identified as related at data generation time. In a real system this would be computed by a clustering job, not stored as a field on individual records.

**Why `email_domain_type` as a category?** Disposable email detection is a lookup operation (match against a maintained list of throwaway domains), not an inference. It belongs in the data layer, not the model layer. Pre-computing it at schema time makes downstream feature engineering cleaner.

**Why separate `hours_to_quota_exhaustion` from `quota_exhausted_at`?** The raw timestamp is useful for time-series analysis. The computed duration is useful as a model feature. Both are worth storing; the duration should not be recomputed in every notebook.

**Why pipe-delimited `abuse_signals`?** Signals are a variable-length set. Storing as a delimited string is a deliberate denormalization for CSV compatibility. In a production system this would be a separate `account_signals` table.

---

## Simulated Data Distributions

The generator (`simulate_abuse_accounts.py`) produces a dataset with approximately:
- 80% `clean` accounts
- 12% `suspected` accounts
- 8% `high_confidence_abuse` accounts
- Overall abuse rate (suspected + high confidence): ~20%, consistent with Stripe's 2026 first-party fraud estimates

Abuse accounts are generated in clusters of 2–6, sharing device fingerprints and showing correlated behavioral patterns (fast quota exhaustion, low return rate, narrow feature use).

---

*Next: [Simulate abuse accounts](simulate_abuse_accounts.py)*
