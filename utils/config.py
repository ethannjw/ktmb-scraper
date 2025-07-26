from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import date, time
from enum import Enum


# Direction constants based on KTMB Shuttle routes
class Direction(str, Enum):
    JB_TO_SG = "JB_TO_SG"
    SG_TO_JB = "SG_TO_JB"


DIRECTION_MAPPING = {
    Direction.JB_TO_SG: "JB Sentral - Woodlands",
    Direction.SG_TO_JB: "Woodlands - JB Sentral",
}


# Time slot constants for filtering desired timings
class TimeSlot(str, Enum):
    EARLY_MORNING = "early_morning"  # 05:00 - 08:59
    MORNING = "morning"  # 09:00 - 11:59
    AFTERNOON = "afternoon"  # 12:00 - 17:59
    EVENING = "evening"  # 18:00 - 21:59
    NIGHT = "night"  # 22:00 - 04:59


TIME_SLOT_RANGES = {
    TimeSlot.EARLY_MORNING: (time(5, 0), time(8, 59)),
    TimeSlot.MORNING: (time(9, 0), time(11, 59)),
    TimeSlot.AFTERNOON: (time(12, 0), time(17, 59)),
    TimeSlot.EVENING: (time(18, 0), time(21, 59)),
    TimeSlot.NIGHT: (time(22, 0), time(4, 59)),
}

# Browser configuration
BROWSER_CONFIG = {
    "headless": True,
    "timeout": 30000,
    "viewport": {"width": 1280, "height": 720},
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

# Website selectors and URLs
KTMB_CONFIG = {
    "base_url": "https://shuttleonline.ktmb.com.my/Home/Shuttle",
    "selectors": {
        "direction_dropdown": "select[name='Direction']",
        "depart_date": "input[name='DepartDate']",
        "return_date": "input[name='ReturnDate']",
        "adult_pax": "select[name='Adult']",
        "child_pax": "select[name='Child']",
        "search_button": "input[type='submit'][value='Search']",
        "train_table": "table.table-striped",
        "train_rows": "table.table-striped tbody tr",
        "loading_indicator": ".loading",
    },
}


class ScraperSettings(BaseModel):
    direction: Direction
    depart_date: date
    return_date: Optional[date] = None
    num_adults: int = Field(default=1, ge=1, le=9)
    num_children: int = Field(default=0, ge=0, le=9)
    desired_time_slots: List[TimeSlot] = Field(default_factory=lambda: list(TimeSlot))
    min_available_seats: int = Field(default=1, ge=1)

    @validator("return_date")
    def validate_return_date(cls, v, values):
        if v and "depart_date" in values and v < values["depart_date"]:
            raise ValueError("Return date must be after depart date")
        return v

    @validator("depart_date")
    def validate_depart_date(cls, v):
        if v < date.today():
            raise ValueError("Depart date cannot be in the past")
        return v

    @property
    def total_pax(self) -> int:
        return self.num_adults + self.num_children


class TrainTiming(BaseModel):
    departure_time: str
    arrival_time: str
    available_seats: int
    train_number: str
    time_slot: TimeSlot
    is_available: bool


class ScrapingResult(BaseModel):
    success: bool
    departure_trains: List[TrainTiming] = Field(default_factory=list)
    return_trains: List[TrainTiming] = Field(default_factory=list)
    error_message: Optional[str] = None
    scraped_at: str
