"""Test validation of fUSI-BIDS example datasets."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from fusi_bids_pydantic import FUSISidecar


def load_json(path: Path) -> dict:
    """Load a JSON file."""
    with open(path) as f:
        return json.load(f)


def find_pwd_jsons(dataset_path: Path) -> list[Path]:
    """Find all PWD JSON files in the dataset, excluding the top-level pwd.json.

    Assumes that JSON files are named like `sub-<label>_task-<label>_pwd.json`
    and that there is only one top-level pwd.json file and no other _pwd.json files
    """
    return sorted(dataset_path.rglob("*_pwd.json"))


def get_unique_contents(json_paths: list[Path]) -> list[Path]:
    """Filter JSON paths to only those with unique contents."""
    content_map = {}
    unique_paths = []

    for path in json_paths:
        content = json.dumps(load_json(path), sort_keys=True)
        if content not in content_map:
            content_map[content] = path
            unique_paths.append(path)

    return unique_paths


@pytest.fixture
def dataset_path() -> Path:
    """Path to the example dataset."""
    return Path(__file__).parent / "fusi-bids-examples" / "datasets" / "0.0.10"


@pytest.fixture
def pwd_json(dataset_path: Path) -> dict:
    """Load the top-level pwd.json file."""
    return load_json(dataset_path / "pwd.json")


# The example datasets do not contain all recommended fields, so we ignore warnings
@pytest.mark.filterwarnings(
    "ignore:RECOMMENDED field probe_manufacturer is not set:UserWarning"
)
@pytest.mark.filterwarnings(
    "ignore:RECOMMENDED field probe_elevation_width_mm is not set:UserWarning"
)
@pytest.mark.filterwarnings(
    "ignore:RECOMMENDED field slice_encoding_direction is not set:UserWarning"
)
@pytest.mark.filterwarnings(
    "ignore:RECOMMENDED field institution_name is not set:UserWarning"
)
@pytest.mark.filterwarnings(
    "ignore:RECOMMENDED field institution_address is not set:UserWarning"
)
@pytest.mark.filterwarnings(
    "ignore:RECOMMENDED field institutional_department_name is not set:UserWarning"
)
@pytest.mark.filterwarnings(
    "ignore:RECOMMENDED field delay_after_trigger_s is not set:UserWarning"
)
def test_validate_example_sidecars(dataset_path: Path, pwd_json: dict):
    """Test that all example sidecar JSONs are valid when merged with pwd.json."""
    pwd_jsons = find_pwd_jsons(dataset_path)
    # Some of the example sidecars are the same, so we only need to validate unique ones
    unique_jsons = get_unique_contents(pwd_jsons)

    print(
        f"Validating {len(unique_jsons)} unique JSON files out of {len(pwd_jsons)} total files"
    )

    for json_path in unique_jsons:
        # Load the individual JSON
        individual_json = load_json(json_path)

        # Merge with top-level pwd.json
        merged_json = {**pwd_json, **individual_json}

        try:
            # Validate with FUSISidecar model
            sidecar = FUSISidecar.model_validate(merged_json)

            # Basic checks
            assert sidecar.manufacturer == pwd_json["Manufacturer"]
            assert sidecar.task_name == individual_json["TaskName"]

            print(f"✓ Validated {json_path.relative_to(dataset_path)}")

        except ValidationError as error:
            pytest.fail(f"Validation failed for {json_path}: {error}")
