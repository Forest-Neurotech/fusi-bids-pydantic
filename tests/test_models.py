"""Unit tests for fUSI-BIDS Pydantic models."""

import pytest
from pydantic import ValidationError

from fusi_bids_pydantic import (
    ClutterFiltering,
    FUSISidecar,
    Hardware,
    InstitutionInformation,
    PowerDopplerIntegration,
    SequenceSpecifics,
    SliceEncodingDirection,
    TaskInformation,
    TimingOptionA,
    TimingOptionB,
    TimingOptionC,
    TimingOptionD,
    TimingOptionE,
    TimingParameters,
)


@pytest.fixture
def hardware_data():
    """Valid hardware data fixture."""
    return {
        # Scanner hardware
        "Manufacturer": "Example Manufacturer",
        "ManufacturersModelName": "Example Model",
        "DeviceSerialNumber": "123456",
        "StationName": "Scanner1",
        "SoftwareVersions": "1.0.0",
        # Probe hardware
        "ProbeManufacturer": "Example Probe Manufacturer",
        "ProbeType": "linear",
        "ProbeModel": "Example Probe Model",
        "ProbeSerialNumber": "PROBE123456",
        "ProbeCentralFrequency": 15.0,
        "ProbeNumberOfElements": [32, 32],
        "ProbePitch": 0.3,
        "ProbeRadiusOfCurvature": 180.0,
        "ProbeElevationWidth": 0.5,
        "ProbeElevationAperture": 1.0,
        "ProbeElevationFocus": 2.0,
    }


@pytest.fixture
def sequence_data():
    """Valid sequence specifics data fixture."""
    return {
        "Depth": [4.0, 14.0],
        "UltrasoundTransmitFrequency": 15.0,
        "UltrasoundPulseRepetitionFrequency": 1000.0,
        "PlaneWaveElevationAngles": [-10.0, 0.0, 10.0],
        "PlaneWaveAzimuthAngles": [-5.0, 0.0, 5.0],
        "UltrafastSamplingFrequency": 333.33,
        "SequenceName": "Example Sequence",
    }


@pytest.fixture
def clutter_filtering_data():
    """Valid clutter filtering data fixture."""
    return {
        "ClutterFilterWindowDuration": 100.0,
        "ClutterFilterWindowStride": 50.0,
        "ClutterFilters": [{"FilterType": "SVD"}],
    }


@pytest.fixture
def power_doppler_data():
    """Valid power Doppler integration data fixture."""
    return {
        "PowerDopplerIntegrationDuration": 100.0,
        "PowerDopplerIntegrationStride": 50.0,
    }


@pytest.fixture
def task_data():
    """Valid task information data fixture."""
    return {
        "TaskName": "rest",
        "TaskDescription": "Resting state acquisition",
        "CogAtlasID": "http://example.com",
    }


@pytest.fixture
def institution_data():
    """Valid institution information data fixture."""
    return {
        "InstitutionName": "Example University",
        "InstitutionAddress": "123 Example St",
        "InstitutionalDepartmentName": "Neuroscience",
    }


@pytest.fixture
def timing_options_common_data():
    """Common data for timing options."""
    return {
        "SliceEncodingDirection": "i",
        "DelayAfterTrigger": 0.5,
    }


@pytest.fixture
def timing_option_a_data(timing_options_common_data):
    """Valid timing option A data fixture."""
    return {
        "RepetitionTime": 1.5,
        **timing_options_common_data,
    }


def test_hardware_validation(hardware_data):
    """Test Hardware model validation."""
    # Test valid data
    hardware = Hardware.model_validate(hardware_data)
    assert hardware.manufacturer == hardware_data["Manufacturer"]
    assert (
        hardware.probe_central_frequency_mhz == hardware_data["ProbeCentralFrequency"]
    )
    assert hardware.probe_number_of_elements == hardware_data["ProbeNumberOfElements"]
    assert hardware.probe_serial_number == hardware_data["ProbeSerialNumber"]

    # Test invalid probe radius of curvature
    with pytest.raises(ValidationError):
        Hardware.model_validate({**hardware_data, "ProbeRadiusOfCurvature": 361.0})

    # Test ProbePitch as array
    pitch_array_data = {**hardware_data, "ProbePitch": [0.3, 0.4]}
    hardware = Hardware.model_validate(pitch_array_data)
    assert hardware.probe_pitch_mm == pitch_array_data["ProbePitch"]


def test_sequence_specifics_validation(sequence_data):
    """Test SequenceSpecifics model validation."""
    # Test valid data
    seq = SequenceSpecifics.model_validate(sequence_data)
    assert seq.depth_mm == sequence_data["Depth"]
    assert (
        seq.plane_wave_elevation_angles_deg == sequence_data["PlaneWaveElevationAngles"]
    )
    assert seq.plane_wave_azimuth_angles_deg == sequence_data["PlaneWaveAzimuthAngles"]
    assert (
        seq.ultrasound_transmit_frequency_mhz
        == sequence_data["UltrasoundTransmitFrequency"]
    )

    # Test invalid depth (max < min)
    with pytest.raises(ValidationError):
        SequenceSpecifics.model_validate({**sequence_data, "Depth": [14.0, 4.0]})

    # Test plane wave angles validation (arrays of different lengths)
    with pytest.raises(ValidationError):
        SequenceSpecifics.model_validate({
            **sequence_data,
            "PlaneWaveElevationAngles": [-10.0, 0.0, 10.0],
            "PlaneWaveAzimuthAngles": [-5.0, 0.0],  # Different length
        })


def test_clutter_filtering_validation(clutter_filtering_data):
    """Test ClutterFiltering model validation."""
    cf = ClutterFiltering.model_validate(clutter_filtering_data)
    assert (
        cf.clutter_filter_window_duration_ms
        == clutter_filtering_data["ClutterFilterWindowDuration"]
    )
    assert (
        cf.clutter_filter_window_stride_ms
        == clutter_filtering_data["ClutterFilterWindowStride"]
    )
    assert len(cf.clutter_filters) == len(clutter_filtering_data["ClutterFilters"])
    assert (
        cf.clutter_filters[0].filter_type
        == clutter_filtering_data["ClutterFilters"][0]["FilterType"]
    )

    # Test stride defaults to duration when not specified
    single_param_data = clutter_filtering_data.copy()
    single_param_data.pop("ClutterFilterWindowStride")
    cf = ClutterFiltering.model_validate(single_param_data)
    assert (
        cf.clutter_filter_window_stride_ms
        == single_param_data["ClutterFilterWindowDuration"]
    )


def test_power_doppler_integration_validation(power_doppler_data):
    """Test PowerDopplerIntegration model validation."""
    # Test with both duration and stride
    pdi = PowerDopplerIntegration.model_validate(power_doppler_data)
    assert (
        pdi.power_doppler_integration_duration_ms
        == power_doppler_data["PowerDopplerIntegrationDuration"]
    )
    assert (
        pdi.power_doppler_integration_stride_ms
        == power_doppler_data["PowerDopplerIntegrationStride"]
    )

    # Test stride defaults to duration when not specified
    single_param_data = {"PowerDopplerIntegrationDuration": 100.0}
    pdi = PowerDopplerIntegration.model_validate(single_param_data)
    assert (
        pdi.power_doppler_integration_stride_ms
        == single_param_data["PowerDopplerIntegrationDuration"]
    )


def test_timing_options(timing_option_a_data, timing_options_common_data):
    """Test various timing options validation."""
    # Test Option A (RepetitionTime only)
    timing_a = TimingOptionA.model_validate(timing_option_a_data)
    assert timing_a.repetition_time_s == timing_option_a_data["RepetitionTime"]

    # Test Option B (SliceTiming and VolumeTiming)
    timing_option_b_data = {
        "SliceTiming": [0.0, 0.1, 0.2],
        "VolumeTiming": [0.0, 1.0, 2.0],
        **timing_options_common_data,
    }

    timing_b = TimingOptionB.model_validate(timing_option_b_data)
    assert timing_b.slice_timing_s == timing_option_b_data["SliceTiming"]
    assert timing_b.volume_timing_s == timing_option_b_data["VolumeTiming"]

    # Test Option C (AcquisitionDuration and VolumeTiming)
    option_c = {
        "AcquisitionDuration": 0.5,
        "VolumeTiming": [0.0, 1.0, 2.0],
        **timing_options_common_data,
    }
    timing_c = TimingOptionC.model_validate(option_c)
    assert timing_c.acquisition_duration_s == option_c["AcquisitionDuration"]
    assert timing_c.volume_timing_s == option_c["VolumeTiming"]

    # Test Option D (RepetitionTime and SliceTiming)
    option_d = {
        "RepetitionTime": 1.5,
        "SliceTiming": [0.0, 0.1, 0.2],
        **timing_options_common_data,
    }
    timing_d = TimingOptionD.model_validate(option_d)
    assert timing_d.repetition_time_s == option_d["RepetitionTime"]
    assert timing_d.slice_timing_s == option_d["SliceTiming"]

    # Test Option E (RepetitionTime and DelayTime)
    option_e = {
        "RepetitionTime": 1.5,
        "DelayTime": 0.5,
        **timing_options_common_data,
    }
    timing_e = TimingOptionE.model_validate(option_e)
    assert timing_e.repetition_time_s == option_e["RepetitionTime"]
    assert timing_e.delay_time_s == option_e["DelayTime"]

    # Test invalid combinations
    with pytest.raises(ValidationError, match="must not have acquisition_duration_s"):
        TimingOptionB.model_validate({
            "SliceTiming": [0.0, 0.1, 0.2],
            "VolumeTiming": [0.0, 1.0, 2.0],
            "AcquisitionDuration": 0.2,  # forbidden in Option B
            **timing_options_common_data,
        })

    with pytest.raises(ValidationError, match="monotonically increasing"):
        TimingOptionB.model_validate({
            "SliceTiming": [0.0, 0.1, 0.2],
            "VolumeTiming": [0.0, 2.0, 1.0],  # not monotonically increasing
            **timing_options_common_data,
        })

    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        TimingOptionB.model_validate({
            "SliceTiming": [0.0, 0.1, 0.2],
            "VolumeTiming": [-1.0, 0.0, 1.0],  # negative value
            **timing_options_common_data,
        })

    # Test missing required fields
    with pytest.raises(ValidationError, match="requires volume_timing_s"):
        TimingOptionB.model_validate({
            "SliceTiming": [0.0, 0.1, 0.2],
            **timing_options_common_data,
        })


def test_task_information_validation(task_data):
    """Test TaskInformation model validation."""
    task = TaskInformation.model_validate(task_data)
    assert task.task_name == "rest"
    assert task.task_description == "Resting state acquisition"

    # Test required TaskName
    with pytest.raises(ValidationError):
        TaskInformation.model_validate({"TaskDescription": "test"})


def test_institution_information_validation(institution_data):
    """Test InstitutionInformation model validation."""
    inst = InstitutionInformation.model_validate(institution_data)
    assert inst.institution_name == "Example University"
    assert inst.institution_address == "123 Example St"


def test_complete_sidecar_validation(
    hardware_data,
    sequence_data,
    clutter_filtering_data,
    power_doppler_data,
    task_data,
    timing_option_a_data,
    institution_data,
):
    """Test complete FUSISidecar model validation."""
    valid_data = {
        **task_data,
        **hardware_data,
        **sequence_data,
        **clutter_filtering_data,
        **power_doppler_data,
        **timing_option_a_data,
        **institution_data,
    }
    sidecar = FUSISidecar.model_validate(valid_data)
    assert sidecar.task_name == task_data["TaskName"]
    assert sidecar.repetition_time_s == timing_option_a_data["RepetitionTime"]
    assert sidecar.manufacturer == hardware_data["Manufacturer"]


def test_slice_encoding_direction_validation(timing_options_common_data):
    """Test SliceEncodingDirection enum validation."""
    assert SliceEncodingDirection.FIRST == "i"
    assert SliceEncodingDirection.SECOND == "j"
    assert SliceEncodingDirection.THIRD == "k"
    assert SliceEncodingDirection.FIRST_REVERSE == "i-"
    assert SliceEncodingDirection.SECOND_REVERSE == "j-"
    assert SliceEncodingDirection.THIRD_REVERSE == "k-"

    # Test in TimingParameters
    valid_data = {
        "RepetitionTime": 1.5,
        **timing_options_common_data,
    }
    timing = TimingParameters.model_validate(valid_data)
    assert timing.slice_encoding_direction == SliceEncodingDirection.FIRST

    # Test invalid direction
    invalid_data = valid_data.copy()
    invalid_data["SliceEncodingDirection"] = "x"
    with pytest.raises(ValidationError):
        TimingParameters.model_validate(invalid_data)
