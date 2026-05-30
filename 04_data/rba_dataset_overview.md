# RBA Dataset Overview

## Source

**Dataset:** [Risk-Based Authentication (RBA) Dataset](https://www.kaggle.com/datasets/dasgroup/rba-dataset)
**Platform:** Kaggle
**Provider:** DAS Group

This dataset contains login event records from a real-world web application, including device and network characteristics captured at authentication time. It was published for research into risk-based authentication systems — the practice of using contextual signals to assess whether a login attempt is likely legitimate before granting access.

## Why This Dataset

Ghost-watcher needs a realistic device fingerprint layer: realistic IP addresses, user agents, operating systems, browser types, and network round-trip times. Generating these from scratch would produce unrealistically uniform distributions.

The RBA dataset provides this layer authentically. It was not collected for abuse detection purposes, so it carries no pre-existing abuse labels that would bias the analysis. The abuse and behavioral layers are simulated on top of it.

## Contents

The dataset includes the following fields relevant to this project:

| Field | Description | Use in ghost-watcher |
|-------|-------------|---------------------|
| `ip_address` | Login IP address | Device fingerprint layer |
| `country` | Country resolved from IP | Geographic signal |
| `asn` | Autonomous System Number | ISP / VPN / datacenter classification |
| `user_agent` | Full browser user agent string | Device fingerprint |
| `os_name` | Operating system name | Device fingerprint |
| `browser_name` | Browser name | Device fingerprint |
| `device_type` | Desktop / Mobile / Tablet | Device fingerprint |
| `round_trip_time_ms` | Network RTT in milliseconds | Latency signal; proxies inflate this |
| `is_attack_ip` | Whether the IP is flagged in threat intelligence | Not used — different threat model |

## What the Dataset Does NOT Contain

The RBA dataset does not contain:
- Account creation events (only login events)
- Usage or behavioral data (no session depth, API calls, quota)
- Conversion or billing information
- Any concept of "account abuse" relevant to subscription cycling

All of these are simulated in `simulate_abuse_accounts.py`.

## How It Is Used

The simulation script samples rows from the RBA dataset to produce realistic device fingerprints for simulated accounts. Abuse accounts are constructed to share device fingerprints (same OS/browser/UA) across multiple accounts. Clean accounts have randomly sampled, unique-ish fingerprints.

This means the device fingerprint distribution in the simulated dataset reflects real-world variation in operating systems, browsers, and network characteristics — including realistic fingerprint collision rates between unrelated users.

## Data Handling

Per the project's data rules:
- The raw RBA dataset is never committed to this repository (listed in `.gitignore`)
- Download it from Kaggle and place it at `data/rba_dataset.csv` before running `simulate_abuse_accounts.py`
- The simulated output (`data/simulated_users.csv`) is also gitignored by default

## Dataset Citation

If using this dataset in published work, cite per Kaggle's standard attribution for this dataset. See the [Kaggle dataset page](https://www.kaggle.com/datasets/dasgroup/rba-dataset) for current citation guidance.

---

*Next: [Schema design](schema_design.md)*
