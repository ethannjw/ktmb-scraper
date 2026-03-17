"""
Holiday-aware travel date logic for KTMB scraper.

Uses the `holidays` library for Singapore public holidays and supports
custom overrides via a JSON file. The core function `get_travel_dates_for_week`
determines which outbound/return dates to search given a Friday anchor date.

Rules:
- If Friday is a holiday, REPLACE the outbound with Thursday.
- If Thursday is also a holiday, walk back further (Wednesday, etc.).
- If Monday is a holiday, ADD Monday as an additional return date.
- Normal weekend: outbound=Friday, return=Sunday.
"""

import json
import logging
import os
from datetime import date, timedelta
from typing import List, Optional, Set, Tuple

import holidays as holidays_lib

logger = logging.getLogger(__name__)

# Type alias
TravelPair = Tuple[date, date]


def get_holidays(
    years: int | List[int],
    custom_holidays_path: Optional[str] = None,
) -> Set[date]:
    """
    Get Singapore public holidays for the given year(s), with optional
    custom overrides from a JSON file.

    Args:
        years: A single year or list of years to load holidays for.
        custom_holidays_path: Path to a JSON file with "add" and "remove" lists.
            Defaults to CUSTOM_HOLIDAYS_PATH env var, then ./custom_holidays.json.

    Returns:
        Set of holiday dates.
    """
    if isinstance(years, int):
        years = [years]

    # Load SG holidays
    sg_holidays = holidays_lib.Singapore(years=years)
    holiday_set: Set[date] = set(sg_holidays.keys())

    logger.info(
        f"Loaded {len(holiday_set)} SG holidays for {years}"
    )

    # Apply custom overrides
    if custom_holidays_path is None:
        custom_holidays_path = os.getenv(
            "CUSTOM_HOLIDAYS_PATH", "./custom_holidays.json"
        )

    if os.path.exists(custom_holidays_path):
        try:
            with open(custom_holidays_path, "r") as f:
                overrides = json.load(f)

            added = overrides.get("add", [])
            removed = overrides.get("remove", [])

            for d in added:
                parsed = date.fromisoformat(d)
                holiday_set.add(parsed)
                logger.debug(f"Custom holiday added: {parsed}")

            for d in removed:
                parsed = date.fromisoformat(d)
                holiday_set.discard(parsed)
                logger.debug(f"Custom holiday removed: {parsed}")

            logger.info(
                f"Applied custom overrides: +{len(added)}, -{len(removed)}"
            )
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse custom holidays file: {e}")
    else:
        logger.debug(f"No custom holidays file at {custom_holidays_path}")

    return holiday_set


def get_travel_dates_for_week(
    friday_date: date,
    holiday_set: Set[date],
    max_walkback: int = 3,
) -> List[TravelPair]:
    """
    Given a Friday date and a set of holidays, determine the outbound and
    return travel date pairs for that week.

    Rules:
    - Normal: outbound=Friday, return=Sunday
    - If Friday is a holiday: replace outbound with Thursday (walk back)
    - If Thursday is also a holiday: walk back further (Wed, etc.)
    - If Monday is a holiday: ADD Monday as an additional return date
    - Outbound is always SG→JB, return is always JB→SG

    Args:
        friday_date: The Friday anchor date (must be a Friday).
        holiday_set: Set of holiday dates to check against.
        max_walkback: Maximum number of days to walk back from Friday.

    Returns:
        List of (outbound_date, return_date) tuples to search.
    """
    if friday_date.weekday() != 4:
        raise ValueError(f"{friday_date} is not a Friday (weekday={friday_date.weekday()})")

    sunday = friday_date + timedelta(days=2)
    monday = friday_date + timedelta(days=3)

    # --- Determine outbound date ---
    outbound = friday_date
    if outbound in holiday_set:
        # Walk back to find the first non-holiday weekday before the weekend
        for i in range(1, max_walkback + 1):
            candidate = friday_date - timedelta(days=i)
            if candidate not in holiday_set:
                outbound = candidate
                holiday_name = _get_holiday_name(friday_date, holiday_set)
                logger.info(
                    f"Friday {friday_date} is a holiday ({holiday_name}), "
                    f"outbound moved to {outbound.strftime('%A, %d %B %Y')}"
                )
                break
        else:
            # If we couldn't walk back far enough, keep the original Friday
            logger.warning(
                f"Could not find a non-holiday day within {max_walkback} days "
                f"before {friday_date}, keeping Friday as outbound"
            )
            outbound = friday_date

    # --- Determine return dates ---
    return_dates = [sunday]

    if monday in holiday_set:
        return_dates.append(monday)
        holiday_name = _get_holiday_name(monday, holiday_set)
        logger.info(
            f"Monday {monday} is a holiday ({holiday_name}), "
            f"adding Monday as additional return date"
        )

    # --- Check if Thursday is a holiday (even if Friday isn't) ---
    thursday = friday_date - timedelta(days=1)
    if thursday in holiday_set and outbound == friday_date:
        # Thursday is a holiday but Friday isn't — this creates a long weekend
        # where people may also travel on Thursday evening
        # For this case, add a Thursday outbound search as well
        pairs = [(thursday, sunday)]
        holiday_name = _get_holiday_name(thursday, holiday_set)
        logger.info(
            f"Thursday {thursday} is a holiday ({holiday_name}), "
            f"adding Thursday outbound search"
        )
        for ret in return_dates:
            pairs.append((friday_date, ret))
        return pairs

    # --- Build the pairs ---
    pairs = []
    for ret in return_dates:
        pairs.append((outbound, ret))

    return pairs


def _get_holiday_name(d: date, holiday_set: Set[date]) -> str:
    """Try to get the holiday name from the holidays library."""
    try:
        sg = holidays_lib.Singapore(years=[d.year])
        name = sg.get(d)
        return name if name else "Public Holiday"
    except Exception:
        return "Public Holiday"


def get_years_for_month(year: int, month: int) -> List[int]:
    """
    Return the list of years needed for holiday lookups for a given month.
    December needs the next year too (for Sunday/Monday spillover).
    """
    years = [year]
    if month == 12:
        years.append(year + 1)
    return years
