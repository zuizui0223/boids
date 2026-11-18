"""v182: fail-closed physical-source admission; never infer datum from EPSG:28992."""
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class PhysicalSourceEvidence:
    dem_vertical_datum: Optional[str] = None
    dem_datum_original_source_url: Optional[str] = None
    gauge_vertical_datum: Optional[str] = None
    gauge_datum_original_source_url: Optional[str] = None
    gauge_to_gps_tidal_transfer_source_url: Optional[str] = None
    gauge_to_gps_tidal_transfer_verified: bool = False
    survey_day_original_source_url: Optional[str] = None
    source_survey_day_verified: bool = False

def physical_admission(e: PhysicalSourceEvidence) -> dict:
    """Return explicit gates. A filename year is not a survey day."""
    datum = bool(
        e.dem_vertical_datum and e.gauge_vertical_datum
        and e.dem_vertical_datum == e.gauge_vertical_datum
        and e.dem_datum_original_source_url
        and e.gauge_datum_original_source_url
    )
    transfer = bool(
        e.gauge_to_gps_tidal_transfer_verified
        and e.gauge_to_gps_tidal_transfer_source_url
    )
    survey = bool(e.source_survey_day_verified and e.survey_day_original_source_url)
    return {
        "common_vertical_datum_source_verified": datum,
        "local_tidal_transfer_source_verified": transfer,
        "actual_survey_day_source_verified": survey,
        "local_water_depth_or_exposure_admitted": datum and transfer and survey,
        "stop_reason": [
            name for name, ok in (
                ("vertical_datum", datum), ("local_tide_transfer", transfer),
                ("actual_survey_day", survey)
            ) if not ok
        ],
    }

if __name__ == "__main__":
    import json
    print("V182_SOURCE_PREFLIGHT=" + json.dumps(
        physical_admission(PhysicalSourceEvidence()), sort_keys=True
    ))
