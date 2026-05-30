"""Synthetic abuse account dataset generator.

Produces a CSV with realistic device fingerprint, account, behavioral,
and label layers for ghost-watcher analysis. Reads device fingerprints
from the Kaggle RBA dataset; generates all other fields synthetically.

Usage:
    python 04_data/simulate_abuse_accounts.py

Output:
    data/simulated_users.csv

Requires:
    data/rba_dataset.csv (download from Kaggle — not committed to repo)
"""

import hashlib
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
RBA_PATH = DATA_DIR / "rba_dataset.csv"
OUTPUT_PATH = DATA_DIR / "simulated_users.csv"

RANDOM_SEED = 42
N_ACCOUNTS = 5_000

# Abuse rate distribution (must sum to 1.0)
FRAC_HIGH_CONFIDENCE_ABUSE = 0.08
FRAC_SUSPECTED = 0.12
FRAC_CLEAN = 0.80

# Cluster sizes for linked abuse accounts
ABUSE_CLUSTER_SIZE_MIN = 2
ABUSE_CLUSTER_SIZE_MAX = 6

# Behavioral parameters by cohort
BEHAVIOR_PARAMS: dict[str, dict] = {
    "high_confidence_abuse": {
        "hours_to_exhaust_mean": 24,
        "hours_to_exhaust_std": 12,
        "days_active_mean": 2.5,
        "days_active_std": 1.5,
        "total_sessions_mean": 8,
        "total_sessions_std": 4,
        "avg_session_duration_mean": 6.0,
        "avg_session_duration_std": 3.0,
        "api_calls_mean": 900,
        "api_calls_std": 300,
        "features_used_mean": 1.5,
        "features_used_std": 0.8,
        "return_after_exhaustion_prob": 0.05,
        "conversion_prob": 0.005,
    },
    "suspected": {
        "hours_to_exhaust_mean": 60,
        "hours_to_exhaust_std": 30,
        "days_active_mean": 6,
        "days_active_std": 4,
        "total_sessions_mean": 18,
        "total_sessions_std": 8,
        "avg_session_duration_mean": 12.0,
        "avg_session_duration_std": 5.0,
        "api_calls_mean": 600,
        "api_calls_std": 200,
        "features_used_mean": 2.5,
        "features_used_std": 1.2,
        "return_after_exhaustion_prob": 0.20,
        "conversion_prob": 0.03,
    },
    "clean": {
        "hours_to_exhaust_mean": 480,
        "hours_to_exhaust_std": 200,
        "days_active_mean": 18,
        "days_active_std": 12,
        "total_sessions_mean": 45,
        "total_sessions_std": 25,
        "avg_session_duration_mean": 22.0,
        "avg_session_duration_std": 10.0,
        "api_calls_mean": 350,
        "api_calls_std": 200,
        "features_used_mean": 5.0,
        "features_used_std": 2.0,
        "return_after_exhaustion_prob": 0.60,
        "conversion_prob": 0.12,
    },
}

DISPOSABLE_DOMAINS = [
    "mailinator.com",
    "guerrillamail.com",
    "10minutemail.com",
    "throwam.com",
    "sharklasers.com",
    "yopmail.com",
    "trashmail.com",
    "tempmail.com",
    "maildrop.cc",
    "dispostable.com",
]

FREE_WEBMAIL_DOMAINS = [
    "gmail.com",
    "yahoo.com",
    "hotmail.com",
    "outlook.com",
    "icloud.com",
    "protonmail.com",
    "aol.com",
    "live.com",
]

CORPORATE_DOMAIN_TEMPLATES = [
    "acme.com",
    "techcorp.io",
    "dataco.net",
    "ventures.co",
    "globalfirm.com",
]

LABEL_VERSION = "v1.0"
OBSERVATION_DATE = datetime(2026, 5, 1)


# ---------------------------------------------------------------------------
# Device fingerprint loading
# ---------------------------------------------------------------------------


def load_rba_fingerprints(path: Path, n: int, rng: np.random.Generator) -> pd.DataFrame:
    """Load and sample device fingerprint rows from the RBA dataset.

    Args:
        path: Path to the RBA CSV file.
        n: Number of fingerprint rows to sample.
        rng: NumPy random generator for reproducibility.

    Returns:
        DataFrame with device fingerprint columns, sampled to n rows.

    Raises:
        FileNotFoundError: If the RBA dataset is not found at the given path.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"RBA dataset not found at {path}.\n"
            "Download from: https://www.kaggle.com/datasets/dasgroup/rba-dataset\n"
            f"Place the CSV at: {path}"
        )

    rba = pd.read_csv(path, low_memory=False)

    # Normalize column names to lowercase with underscores
    rba.columns = rba.columns.str.lower().str.replace(" ", "_").str.replace("-", "_")

    # Select the columns we care about; gracefully handle missing ones
    desired_cols = [
        "ip_address",
        "country",
        "asn",
        "user_agent",
        "os_name",
        "browser_name",
        "device_type",
        "round_trip_time_ms",
    ]
    available_cols = [c for c in desired_cols if c in rba.columns]
    rba = rba[available_cols].dropna(subset=["ip_address"])

    # Sample with replacement if needed
    indices = rng.integers(0, len(rba), size=n)
    return rba.iloc[indices].reset_index(drop=True)


def make_synthetic_fingerprints(n: int, rng: np.random.Generator) -> pd.DataFrame:
    """Generate synthetic device fingerprints when RBA dataset is unavailable.

    Args:
        n: Number of fingerprint rows to generate.
        rng: NumPy random generator.

    Returns:
        DataFrame with synthetic device fingerprint columns.
    """
    os_options = ["Windows 10", "Windows 11", "macOS 14", "macOS 13", "Ubuntu 22.04"]
    browser_options = ["Chrome", "Firefox", "Safari", "Edge"]
    device_options = ["Desktop", "Mobile", "Tablet"]
    device_weights = [0.65, 0.30, 0.05]

    os_choice = rng.choice(os_options, size=n)
    browser_choice = rng.choice(browser_options, size=n)
    device_choice = rng.choice(device_options, size=n, p=device_weights)

    ip_parts = [
        f"{rng.integers(1, 255)}.{rng.integers(0, 255)}.{rng.integers(0, 255)}.{rng.integers(0, 255)}"
        for _ in range(n)
    ]
    asn_numbers = [f"AS{rng.integers(1000, 65000)}" for _ in range(n)]
    rtts = rng.exponential(scale=50, size=n).clip(5, 500)

    return pd.DataFrame(
        {
            "ip_address": ip_parts,
            "country": rng.choice(["US", "GB", "DE", "CA", "FR", "IN", "BR"], size=n),
            "asn": asn_numbers,
            "os_name": os_choice,
            "browser_name": browser_choice,
            "device_type": device_choice,
            "round_trip_time_ms": rtts.round(1),
            "user_agent": [
                f"Mozilla/5.0 ({o}; rv:120.0) Gecko/20100101 {b}/120.0"
                for o, b in zip(os_choice, browser_choice)
            ],
        }
    )


# ---------------------------------------------------------------------------
# Account generation
# ---------------------------------------------------------------------------


def classify_asn_type(asn: str) -> str:
    """Classify an ASN string into a rough category.

    Args:
        asn: ASN string (e.g., 'AS7922').

    Returns:
        One of 'residential', 'datacenter', 'vpn', 'tor'.
    """
    # Simplified heuristic based on ASN number ranges (not accurate for production)
    asn_num = int(asn.replace("AS", "").split()[0]) if asn and asn.startswith("AS") else 0
    if asn_num in range(13335, 13336):  # Cloudflare
        return "datacenter"
    if asn_num in range(14061, 14062):  # DigitalOcean
        return "datacenter"
    # Random assignment weighted toward residential
    r = asn_num % 100
    if r < 75:
        return "residential"
    if r < 88:
        return "datacenter"
    if r < 97:
        return "vpn"
    return "tor"


def generate_email(
    label: str,
    cluster_id: str,
    account_idx: int,
    rng: np.random.Generator,
) -> tuple[str, str, str]:
    """Generate a realistic email address for a simulated account.

    Args:
        label: Abuse confidence tier for this account.
        cluster_id: Cluster identifier (used for abuse accounts sharing patterns).
        account_idx: Position within the cluster.
        rng: NumPy random generator.

    Returns:
        Tuple of (email_address, email_domain, email_domain_type).
    """
    # Abuse accounts heavily use disposable domains
    if label == "high_confidence_abuse":
        domain_type_weights = [0.55, 0.38, 0.05, 0.02]
    elif label == "suspected":
        domain_type_weights = [0.20, 0.65, 0.12, 0.03]
    else:
        domain_type_weights = [0.02, 0.72, 0.20, 0.06]

    domain_type = rng.choice(
        ["disposable", "free_webmail", "corporate", "custom"],
        p=domain_type_weights,
    )

    if domain_type == "disposable":
        domain = rng.choice(DISPOSABLE_DOMAINS)
    elif domain_type == "free_webmail":
        domain = rng.choice(FREE_WEBMAIL_DOMAINS)
    elif domain_type == "corporate":
        domain = rng.choice(CORPORATE_DOMAIN_TEMPLATES)
    else:
        domain = f"user{rng.integers(100, 9999)}.net"

    # Generate username
    username_base = hashlib.md5(f"{cluster_id}{account_idx}".encode()).hexdigest()[:8]
    username = f"{username_base}{rng.integers(10, 999)}"

    return f"{username}@{domain}", domain, domain_type


def generate_account_timestamps(
    label: str,
    cluster_creation_base: datetime,
    account_idx: int,
    rng: np.random.Generator,
) -> tuple[datetime, datetime | None, float | None]:
    """Generate account creation time and quota exhaustion timestamps.

    Args:
        label: Abuse confidence tier.
        cluster_creation_base: Base datetime for the cluster's first account.
        account_idx: Position within cluster (later accounts created later).
        rng: NumPy random generator.

    Returns:
        Tuple of (account_created_at, quota_exhausted_at, hours_to_exhaustion).
    """
    # Abuse accounts in a cluster are created close together
    if label in ("high_confidence_abuse", "suspected"):
        offset_days = float(rng.integers(0, 4)) * account_idx
    else:
        offset_days = float(rng.integers(0, 90))

    account_created_at = cluster_creation_base + timedelta(days=offset_days)

    params = BEHAVIOR_PARAMS[label]
    hours_to_exhaust = max(
        1.0,
        rng.normal(
            params["hours_to_exhaust_mean"],
            params["hours_to_exhaust_std"],
        ),
    )

    # Clean accounts sometimes never exhaust quota
    quota_prob = 0.90 if label == "high_confidence_abuse" else 0.70 if label == "suspected" else 0.35
    if rng.random() < quota_prob:
        quota_exhausted_at = account_created_at + timedelta(hours=float(hours_to_exhaust))
        return account_created_at, quota_exhausted_at, round(hours_to_exhaust, 1)
    else:
        return account_created_at, None, None


def compute_abuse_signals(row: dict) -> list[str]:
    """Determine which abuse signals are present for a given account record.

    Args:
        row: Dictionary of account fields.

    Returns:
        List of signal name strings (empty if clean).
    """
    signals = []

    if row.get("email_domain_type") == "disposable":
        signals.append("disposable_email")

    hours = row.get("hours_to_quota_exhaustion")
    if hours is not None and hours < 48:
        signals.append("fast_quota_exhaust")

    if row.get("accounts_in_cluster", 1) >= 3:
        signals.append("ip_cluster")

    asn_type = row.get("asn_type", "residential")
    if asn_type in ("vpn", "tor", "datacenter") and hours is not None and hours < 96:
        signals.append("datacenter_asn_high_usage")

    if row.get("return_after_exhaustion") is False and row.get("quota_exhausted") is True:
        signals.append("no_return_after_exhaust")

    if row.get("features_used", 5) <= 1:
        signals.append("narrow_feature_use")

    return signals


def assign_label_from_signals(signals: list[str], noise_rate: float = 0.05) -> str:
    """Assign an abuse confidence tier based on triggered signals.

    Args:
        signals: List of triggered signal names.
        noise_rate: Probability of random label noise to simulate real-world imprecision.

    Returns:
        One of 'high_confidence_abuse', 'suspected', 'clean'.
    """
    hard_signals = {"disposable_email", "fast_quota_exhaust", "ip_cluster"}
    n_hard = len(set(signals) & hard_signals)
    n_total = len(signals)

    if n_hard >= 2 and n_total >= 3:
        label = "high_confidence_abuse"
    elif n_hard >= 1 or n_total >= 2:
        label = "suspected"
    else:
        label = "clean"

    # Inject controlled label noise
    if random.random() < noise_rate:
        label = random.choice(["high_confidence_abuse", "suspected", "clean"])

    return label


# ---------------------------------------------------------------------------
# Main simulation
# ---------------------------------------------------------------------------


def simulate_dataset(
    n_accounts: int = N_ACCOUNTS,
    rba_path: Path = RBA_PATH,
) -> pd.DataFrame:
    """Generate the full simulated account dataset.

    Args:
        n_accounts: Total number of accounts to generate.
        rba_path: Path to RBA dataset CSV for device fingerprints.

    Returns:
        DataFrame with all schema layers combined.
    """
    rng = np.random.default_rng(RANDOM_SEED)
    random.seed(RANDOM_SEED)

    n_high = int(n_accounts * FRAC_HIGH_CONFIDENCE_ABUSE)
    n_suspected = int(n_accounts * FRAC_SUSPECTED)
    n_clean = n_accounts - n_high - n_suspected

    label_plan = (
        ["high_confidence_abuse"] * n_high
        + ["suspected"] * n_suspected
        + ["clean"] * n_clean
    )
    rng.shuffle(label_plan)

    # Load or synthesize device fingerprints
    try:
        fingerprints = load_rba_fingerprints(rba_path, n_accounts, rng)
        print(f"Loaded {len(fingerprints)} fingerprints from RBA dataset.")
    except FileNotFoundError as e:
        print(f"Warning: {e}")
        print("Falling back to synthetic fingerprint generation.")
        fingerprints = make_synthetic_fingerprints(n_accounts, rng)

    # Build clusters: group consecutive abuse accounts together
    cluster_map: dict[int, str] = {}
    cluster_size_map: dict[int, int] = {}
    cluster_base_time: dict[int, datetime] = {}

    i = 0
    cluster_counter = 0
    base_date = datetime(2025, 1, 1)

    while i < n_accounts:
        label = label_plan[i]
        if label in ("high_confidence_abuse", "suspected"):
            cluster_size = int(
                rng.integers(ABUSE_CLUSTER_SIZE_MIN, ABUSE_CLUSTER_SIZE_MAX + 1)
            )
            cluster_size = min(cluster_size, n_accounts - i)
            cluster_id = f"cluster_{cluster_counter:04d}"
            creation_base = base_date + timedelta(days=float(rng.integers(0, 400)))
            for j in range(cluster_size):
                if i + j < n_accounts:
                    cluster_map[i + j] = cluster_id
                    cluster_size_map[i + j] = cluster_size
                    cluster_base_time[i + j] = creation_base
            i += cluster_size
            cluster_counter += 1
        else:
            cluster_id = f"cluster_{cluster_counter:04d}"
            cluster_map[i] = cluster_id
            cluster_size_map[i] = 1
            cluster_base_time[i] = base_date + timedelta(days=float(rng.integers(0, 400)))
            i += 1
            cluster_counter += 1

    # Generate per-account records
    records = []
    for idx in range(n_accounts):
        label = label_plan[idx]
        params = BEHAVIOR_PARAMS[label]
        cluster_id = cluster_map[idx]
        cluster_size = cluster_size_map[idx]
        cluster_base = cluster_base_time[idx]

        # Determine position within cluster
        account_idx_in_cluster = sum(
            1 for k in range(idx) if cluster_map.get(k) == cluster_id
        )

        # Device fingerprint row
        fp = fingerprints.iloc[idx]

        # For abuse clusters, share the fingerprint from the first account in cluster
        # Find cluster anchor fingerprint index
        if cluster_size > 1 and label in ("high_confidence_abuse", "suspected"):
            anchor_idx = next(
                k for k in range(idx + 1) if cluster_map.get(k) == cluster_id
            )
            fp = fingerprints.iloc[anchor_idx]

        asn_str = str(fp.get("asn", "AS0"))
        asn_type = classify_asn_type(asn_str)

        email, email_domain, email_domain_type = generate_email(
            label, cluster_id, account_idx_in_cluster, rng
        )

        account_created_at, quota_exhausted_at, hours_to_exhaust = (
            generate_account_timestamps(label, cluster_base, account_idx_in_cluster, rng)
        )

        days_active = max(
            1,
            int(
                rng.normal(params["days_active_mean"], params["days_active_std"])
            ),
        )
        total_sessions = max(
            1,
            int(rng.normal(params["total_sessions_mean"], params["total_sessions_std"])),
        )
        avg_session_duration = max(
            1.0,
            float(
                rng.normal(
                    params["avg_session_duration_mean"],
                    params["avg_session_duration_std"],
                )
            ),
        )
        api_calls = max(
            0,
            int(rng.normal(params["api_calls_mean"], params["api_calls_std"])),
        )
        features_used = max(
            1,
            int(rng.normal(params["features_used_mean"], params["features_used_std"])),
        )

        quota_exhausted = quota_exhausted_at is not None
        return_after_exhaust = (
            bool(rng.random() < params["return_after_exhaustion_prob"])
            if quota_exhausted
            else False
        )

        is_converted = bool(rng.random() < params["conversion_prob"])
        conversion_date = (
            account_created_at + timedelta(days=float(rng.integers(7, 60)))
            if is_converted
            else None
        )

        days_since_active = max(
            0,
            (OBSERVATION_DATE - account_created_at).days - days_active,
        )

        record = {
            # Device fingerprint layer
            "ip_address": str(fp.get("ip_address", "0.0.0.0")),
            "country": str(fp.get("country", "US")),
            "asn": asn_str,
            "asn_type": asn_type,
            "os_name": str(fp.get("os_name", "Unknown")),
            "browser_name": str(fp.get("browser_name", "Unknown")),
            "device_type": str(fp.get("device_type", "Desktop")),
            "user_agent": str(fp.get("user_agent", "")),
            "round_trip_time_ms": float(fp.get("round_trip_time_ms", 50.0)),
            # Account layer
            "account_id": str(uuid.uuid4()),
            "account_created_at": account_created_at.isoformat(),
            "email_address": email,
            "email_domain": email_domain,
            "email_domain_type": email_domain_type,
            "plan_type": "free",
            "is_converted": is_converted,
            "conversion_date": conversion_date.isoformat() if conversion_date else None,
            "linked_account_cluster": cluster_id,
            "accounts_in_cluster": cluster_size,
            # Behavior layer
            "days_active": days_active,
            "total_sessions": total_sessions,
            "avg_session_duration_mins": round(avg_session_duration, 1),
            "api_calls_count": api_calls,
            "features_used": features_used,
            "quota_exhausted": quota_exhausted,
            "quota_exhausted_at": quota_exhausted_at.isoformat() if quota_exhausted_at else None,
            "hours_to_quota_exhaustion": hours_to_exhaust,
            "return_after_exhaustion": return_after_exhaust,
            "days_since_last_active": days_since_active,
        }

        # Compute signals and label
        signals = compute_abuse_signals(record)
        # Override label for clean accounts to reduce false positives
        if label == "clean" and len(signals) > 0:
            signals = []  # Suppress signals for clean accounts in simulation

        assigned_label = assign_label_from_signals(signals)

        record["abuse_confidence"] = assigned_label
        record["abuse_signals"] = "|".join(signals) if signals else ""
        record["label_version"] = LABEL_VERSION
        record["label_source"] = "rule"

        records.append(record)

    df = pd.DataFrame(records)
    return df


def main() -> None:
    """Run the simulation and write output CSV."""
    print(f"Simulating {N_ACCOUNTS} accounts (seed={RANDOM_SEED})...")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    df = simulate_dataset()

    # Summary statistics
    label_counts = df["abuse_confidence"].value_counts()
    print("\nLabel distribution:")
    for label, count in label_counts.items():
        print(f"  {label}: {count} ({count / len(df) * 100:.1f}%)")

    print(f"\nConversion rate: {df['is_converted'].mean():.1%}")
    print(f"Quota exhaustion rate: {df['quota_exhausted'].mean():.1%}")

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nWrote {len(df)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
