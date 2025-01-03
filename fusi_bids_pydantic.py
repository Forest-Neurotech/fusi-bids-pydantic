"""fUSI-BIDS Pydantic models for sidecar JSON schema.

Ported from https://bids.neuroimaging.io/bep040
"""

import warnings
from enum import Enum
from typing import Annotated, Any, ClassVar, Optional, Union

from pydantic import (
    AfterValidator,
    AnyUrl,
    BaseModel,
    ConfigDict,
    Field,
    FiniteFloat,
    NonNegativeFloat,
    PositiveFloat,
    PositiveInt,
    ValidationError,
    ValidationInfo,
    field_validator,
    model_validator,
)


def warn_if_none(value: Any, info: ValidationInfo) -> Any:
    """AfterValidator for RECOMMENDED fields.

    This validator will warn if the field is None.
    """
    if value is None:
        warnings.warn(f"RECOMMENDED field {info.field_name} is not set.", stacklevel=2)
    return value


class Hardware(BaseModel):
    """Scanner and probe hardware information."""

    model_config = ConfigDict(extra="allow", validate_default=True)
    manufacturer: Annotated[Optional[str], AfterValidator(warn_if_none)] = Field(
        None,
        description="Manufacturer of the ultrasound scanner that produced the measurements.",
        alias="Manufacturer",
    )
    manufacturers_model_name: Annotated[Optional[str], AfterValidator(warn_if_none)] = (
        Field(
            None,
            description="Manufacturer's model name of the ultrasound scanner that produced the measurements.",
            alias="ManufacturersModelName",
        )
    )
    device_serial_number: Annotated[Optional[str], AfterValidator(warn_if_none)] = (
        Field(
            None,
            description="The serial number of the ultrasound scanner that produced the measurements. "
            "A pseudonym can also be used to prevent the equipment from being identifiable, "
            "so long as each pseudonym is unique within the dataset.",
            alias="DeviceSerialNumber",
        )
    )
    station_name: Annotated[Optional[str], AfterValidator(warn_if_none)] = Field(
        None,
        description="Institution-defined name of the ultrasound scanner that produced the measurements.",
        alias="StationName",
    )
    software_versions: Annotated[Optional[str], AfterValidator(warn_if_none)] = Field(
        None,
        description="Manufacturer's designation of the software version of the ultrasound scanner "
        "that produced the measurements.",
        alias="SoftwareVersions",
    )
    probe_manufacturer: Annotated[Optional[str], AfterValidator(warn_if_none)] = Field(
        None,
        description="Manufacturer of the ultrasound probe that produced the measurements.",
        alias="ProbeManufacturer",
    )
    probe_type: Annotated[Optional[str], AfterValidator(warn_if_none)] = Field(
        None,
        description="Information describing the ultrasound probe type, e.g. linear, RCA, multiarray, etc.).",
        alias="ProbeType",
    )
    probe_model: Annotated[Optional[str], AfterValidator(warn_if_none)] = Field(
        None,
        description="Manufacturer's model name of the ultrasound probe used to produce the measurements.",
        alias="ProbeModel",
    )
    probe_central_frequency_mhz: Annotated[
        Optional[NonNegativeFloat], AfterValidator(warn_if_none)
    ] = Field(
        None,
        description="Central frequency of the ultrasound probe, in megahertz.",
        alias="ProbeCentralFrequency",
    )
    probe_number_of_elements: Annotated[
        Optional[Union[PositiveInt, list[PositiveInt]]], AfterValidator(warn_if_none)
    ] = Field(
        None,
        description="Number of probe transducers along each probe axis (e.g. [32, 32] for a 32x32 matrix probe).",
        alias="ProbeNumberOfElements",
    )
    probe_pitch_mm: Annotated[Optional[PositiveFloat], AfterValidator(warn_if_none)] = (
        Field(
            None,
            description="Inter-element pitch of the probe, in millimeters.",
            alias="ProbePitch",
        )
    )
    probe_radius_of_curvature_deg: Annotated[
        Optional[float], AfterValidator(warn_if_none)
    ] = Field(
        None,
        description="Radius of curvature of the probe, in degrees.",
        alias="ProbeRadiusOfCurvature",
    )
    probe_elevation_width_mm: Annotated[
        Optional[PositiveFloat], AfterValidator(warn_if_none)
    ] = Field(
        None,
        description="Elevation width at the probe focal point, in millimeters.",
        alias="ProbeElevationWidth",
    )
    probe_elevation_aperture_mm: Annotated[
        Optional[PositiveFloat], AfterValidator(warn_if_none)
    ] = Field(
        None,
        description="Elevation aperture of the probe, in millimeters.",
        alias="ProbeElevationAperture",
    )
    probe_elevation_focus_mm: Annotated[
        Optional[PositiveFloat], AfterValidator(warn_if_none)
    ] = Field(
        None,
        description="Elevation focus of the probe, in millimeters.",
        alias="ProbeElevationFocus",
    )

    @field_validator("probe_radius_of_curvature_deg")
    @classmethod
    def validate_probe_radius_of_curvature(cls, v: float) -> float:
        if (v is not None) and (v < 0 or v > 360):
            raise ValueError(
                "Probe radius of curvature must be between 0 and 360 degrees"
            )
        return v


class SequenceSpecifics(BaseModel):
    """Transmit-receive sequence"""

    model_config = ConfigDict(extra="allow", validate_default=True)
    depth_mm: Annotated[Optional[list[FiniteFloat]], AfterValidator(warn_if_none)] = (
        Field(
            None,
            description="Minimal and maximal depth of the field of view from the probe surface, e.g. [4,14], in millimeters.",
            alias="Depth",
        )
    )
    ultrasound_pulse_repetition_frequency_hz: Annotated[
        Optional[PositiveFloat], AfterValidator(warn_if_none)
    ] = Field(
        None,
        description="Pulse repetition frequency, in hertz.",
        alias="UltrasoundPulseRepetitionFrequency",
    )
    plane_wave_angles_deg: Annotated[
        Optional[Union[FiniteFloat, list[FiniteFloat]]], AfterValidator(warn_if_none)
    ] = Field(
        None,
        description="Angles at which tilted plane waves are emitted, in degrees.",
        alias="PlaneWaveAngles",
    )
    ultrafast_sampling_frequency_hz: Annotated[
        Optional[PositiveFloat], AfterValidator(warn_if_none)
    ] = Field(
        None,
        description="Sampling frequency of the compounded volumes, in hertz. Note that UltrafastSamplingFrequency "
        "should be equal to UltrasoundPulseRepetitionFrequency divided by the number of tilted plane "
        "wave angles defined in PlaneWavesAngles.",
        alias="UltrafastSamplingFrequency",
    )
    compound_virtual_sources: Optional[list[list[float]]] = Field(
        None,
        description="2D array storing the virtual source positions of diverging waves used to generate compounded "
        "ultrasound images. Each source position is expressed relative to the probe center with negative "
        "values in depth for diverging sources.",
        alias="CompoundVirtualSources",
    )
    probe_voltage_v: Optional[PositiveFloat] = Field(
        None,
        description="Voltage applied to the probe, in volts.",
        alias="ProbeVoltage",
    )
    sequence_name: Annotated[Optional[str], AfterValidator(warn_if_none)] = Field(
        None,
        description="Manufacturer's designation of the sequence name.",
        alias="SequenceName",
    )
    transmit_mask: Optional[Union[list[bool], list[list[bool]]]] = Field(
        None,
        description="Element mask for matrix probes where not all elements transmit on each sequence. True if transmitted.",
        alias="TransmitMask",
    )
    receive_mask: Optional[Union[list[bool], list[list[bool]]]] = Field(
        None,
        description="Element mask for matrix probes where not all elements receive on each sequence. True if received.",
        alias="ReceiveMask",
    )

    @field_validator("depth_mm")
    @classmethod
    def validate_depth(cls, v: list[float]) -> list[float]:
        if v is None:
            return v
        if len(v) != 2:
            raise ValueError("Depth must be a list of two values")
        if v[1] <= v[0]:
            err_msg = "Max depth must be greater than min depth"
            raise ValueError(err_msg)
        return v


class ClutterFilter(BaseModel):
    """Clutter filter. Allows for extra parameters."""

    model_config = ConfigDict(extra="allow", validate_default=True)
    filter_type: str = Field(
        ..., description="Type of clutter filter applied", alias="FilterType"
    )


class ClutterFiltering(BaseModel):
    """Clutter filtering."""

    model_config = ConfigDict(extra="allow", validate_default=True)
    clutter_filter_window_duration_ms: Annotated[
        Optional[PositiveFloat], AfterValidator(warn_if_none)
    ] = Field(
        None,
        description="Duration of the clutter filter window, in milliseconds.",
        alias="ClutterFilterWindowDuration",
    )
    clutter_filters: Annotated[
        Optional[list[ClutterFilter]], AfterValidator(warn_if_none)
    ] = Field(
        None,
        description="Clutter filter methods used to remove clutter artifacts.",
        alias="ClutterFilters",
    )


class PowerDopplerIntegration(BaseModel):
    """Power Doppler integration window."""

    model_config = ConfigDict(extra="allow", validate_default=True)
    power_doppler_integration_duration_ms: Annotated[
        Optional[PositiveFloat], AfterValidator(warn_if_none)
    ] = Field(
        None,
        description="Duration of the power Doppler integration window, in milliseconds.",
        alias="PowerDopplerIntegrationDuration",
    )
    power_doppler_integration_stride_ms: Optional[PositiveFloat] = Field(
        None,
        description="Stride from one power Doppler integration window to another, in milliseconds. "
        "Assumed equal to the PowerDopplerIntegrationDuration as default.",
        alias="PowerDopplerIntegrationStride",
    )

    @model_validator(mode="after")
    def stride_defaults_to_duration(self) -> "PowerDopplerIntegration":
        """If unset, assume PowerDopplerIntegrationStride is equal to PowerDopplerIntegrationDuration."""
        if self.power_doppler_integration_stride_ms is None:
            self.power_doppler_integration_stride_ms = (
                self.power_doppler_integration_duration_ms
            )
        return self


class SliceEncodingDirection(str, Enum):
    """Valid slice encoding directions."""

    FIRST = "i"
    SECOND = "j"
    THIRD = "k"
    FIRST_REVERSE = "i-"
    SECOND_REVERSE = "j-"
    THIRD_REVERSE = "k-"


class TimingParametersBase(BaseModel):
    """Timing parameters base model."""

    model_config = ConfigDict(extra="allow", validate_default=True)
    volume_timing_s: Optional[list[NonNegativeFloat]] = Field(
        None,
        description="The time at which each volume was acquired during the acquisition. "
        "It is described using a list of times referring to the onset of each volume in the series. "
        "The list must have the same length as the series, and the values must be "
        "non-negative and monotonically increasing. This field is mutually exclusive with "
        "'RepetitionTime'. This field is mutually exclusive with 'DelayTime'. If defined, "
        "this requires acquisition time (TA) be defined via either 'SliceTiming' or 'AcquisitionDuration'.",
        alias="VolumeTiming",
    )
    repetition_time_s: Optional[float] = Field(
        None,
        description="The time in seconds between the beginning of an acquisition of one volume "
        "and the beginning of acquisition of the volume following it. This definition "
        "includes time between scans (when no data has been acquired) in case of sparse "
        "acquisition schemes. This value MUST be consistent with the 'pixdim[4]' field "
        "(after accounting for units stored in 'xyzt_units' field) in the NIfTI header. "
        "This field is mutually exclusive with VolumeTiming.",
        alias="RepetitionTime",
        gt=0,
    )
    slice_timing_s: Optional[list[float]] = Field(
        None,
        description="The time at which each slice was acquired within each volume (frame) of "
        "the acquisition. Slice timing is not slice order -- rather, it is a list of times "
        "containing the time (in seconds) of each slice acquisition in relation to the "
        "beginning of volume acquisition. The list goes through the slices along the slice "
        "axis in the slice encoding dimension (see below). Note that to ensure the proper "
        "interpretation of the 'SliceTiming' field, it is important to check if "
        "SliceEncodingDirection exists. In particular, if 'SliceEncodingDirection' is "
        "negative, the entries in 'SliceTiming' are defined in reverse order with respect "
        "to the slice axis, such that the final entry in the 'SliceTiming' list is the "
        "time of acquisition of slice 0. Without this parameter slice time correction will "
        "not be possible.",
        alias="SliceTiming",
    )
    slice_encoding_direction: Annotated[
        Optional[SliceEncodingDirection], AfterValidator(warn_if_none)
    ] = Field(
        None,
        description="The axis of the NIfTI data along which slices were acquired, and the "
        "direction in which 'SliceTiming' is defined with respect to. i, j, k identifiers "
        "correspond to the first, second and third axis of the data in the NIfTI file. "
        "A - sign indicates that the contents of 'SliceTiming' are defined in reverse "
        "order - that is, the first entry corresponds to the slice with the largest index, "
        "and the final entry corresponds to slice index zero. When present, the axis "
        "defined by 'SliceEncodingDirection' needs to be consistent with the slice_dim "
        "field in the NIfTI header. When absent, the entries in 'SliceTiming' must be in "
        "the order of increasing slice index as defined by the NIfTI header.",
        alias="SliceEncodingDirection",
    )
    delay_time_s: Optional[float] = Field(
        None,
        description="User specified time (in seconds) to delay the acquisition of data for "
        "the following volume. If the field is not present it is assumed to be set to zero. "
        "This field is REQUIRED for sparse sequences using the 'RepetitionTime' field that "
        "do not have the 'SliceTiming' field set to allow for accurate calculation of "
        "'acquisition time'. This field is mutually exclusive with 'VolumeTiming'.",
        alias="DelayTime",
        ge=0,
    )
    acquisition_duration_s: Optional[float] = Field(
        None,
        description="Duration (in seconds) of volume acquisition. This field is mutually "
        "exclusive with 'RepetitionTime'. Must be a number greater than 0.",
        alias="AcquisitionDuration",
        gt=0,
    )
    delay_after_trigger_s: Annotated[Optional[float], AfterValidator(warn_if_none)] = (
        Field(
            None,
            description="Duration (in seconds) from trigger delivery to scan onset. This delay "
            "is commonly caused by adjustments, loading times, or robot movement.",
            alias="DelayAfterTrigger",
            ge=0,
        )
    )

    @field_validator("volume_timing_s")
    @classmethod
    def validate_volume_timing_monotonic(cls, v: list[float]) -> list[float]:
        if (v is not None) and (not all(v[i] <= v[i + 1] for i in range(len(v) - 1))):
            raise ValueError("Values must be monotonically increasing")
        return v

    @field_validator("delay_time_s")
    @classmethod
    def validate_delay_time(
        cls, v: Optional[float], info: ValidationInfo
    ) -> Optional[float]:
        volume_timing_s = info.data.get("volume_timing_s")
        if (v is not None) and (volume_timing_s is not None):
            raise ValueError("DelayTime is mutually exclusive with VolumeTiming")
        if (v is None) and (volume_timing_s is None):
            # Defaults to 0 if not set
            return 0.0
        return v

    @field_validator("acquisition_duration_s")
    @classmethod
    def validate_acquisition_duration(
        cls, v: Optional[float], info: ValidationInfo
    ) -> Optional[float]:
        """Mutually exclusive with RepetitionTime."""
        repetition_time_s = info.data.get("repetition_time_s")
        if (v is not None) and (repetition_time_s is not None):
            raise ValueError(
                "Acquisition duration is mutually exclusive with RepetitionTime"
            )
        return v


class TimingOptionConfigError(ValueError):
    """Error for invalid timing configuration for a given option."""

    def __init__(self, option_name: str, message: str):
        self.option_name = option_name
        self.message = message
        super().__init__(f"Invalid timing configuration for {option_name}: {message}")


class TimingOptionBase(TimingParametersBase):
    """Base class for timing options with shared validation logic."""

    model_config = ConfigDict(extra="allow", validate_default=True)

    required_fields: ClassVar[set[str]] = set()
    forbidden_fields: ClassVar[set[str]] = set()

    @model_validator(mode="after")
    def validate_timing_requirements(self) -> "TimingOptionBase":
        # Check required fields
        missing_fields = [
            field for field in self.required_fields if getattr(self, field) is None
        ]
        if missing_fields:
            raise TimingOptionConfigError(
                self.__class__.__name__, f"requires {', '.join(missing_fields)}"
            )

        # Check forbidden fields
        present_forbidden = [
            field for field in self.forbidden_fields if getattr(self, field) is not None
        ]
        if present_forbidden:
            raise TimingOptionConfigError(
                self.__class__.__name__, f"must not have {', '.join(present_forbidden)}"
            )
        return self


class TimingOptionA(TimingOptionBase):
    """Timing option A."""

    required_fields = {"repetition_time_s"}
    forbidden_fields = {"acquisition_duration_s", "volume_timing_s"}


class TimingOptionB(TimingOptionBase):
    """Timing option B."""

    required_fields = {"slice_timing_s", "volume_timing_s"}
    forbidden_fields = {"repetition_time_s", "acquisition_duration_s", "delay_time_s"}


class TimingOptionC(TimingOptionBase):
    """Timing option C."""

    required_fields = {"acquisition_duration_s", "volume_timing_s"}
    forbidden_fields = {"repetition_time_s", "slice_timing_s", "delay_time_s"}


class TimingOptionD(TimingOptionBase):
    """Timing option D."""

    required_fields = {"repetition_time_s", "slice_timing_s"}
    forbidden_fields = {"acquisition_duration_s", "volume_timing_s"}


class TimingOptionE(TimingOptionBase):
    """Timing option E."""

    required_fields = {"repetition_time_s", "delay_time_s"}
    forbidden_fields = {"slice_timing_s", "acquisition_duration_s", "volume_timing_s"}


class TimingParameters(TimingParametersBase):
    """Base model that validates against all timing options."""

    @model_validator(mode="after")
    def validate_timing_options(self) -> "TimingParameters":
        data = self.model_dump(by_alias=True, round_trip=True, exclude_unset=True)
        errors = []

        # Try each timing option
        for option_class in (
            TimingOptionA,
            TimingOptionB,
            TimingOptionC,
            TimingOptionD,
            TimingOptionE,
        ):
            try:
                option_class.model_validate(data)
            except ValidationError as err:
                errors.append(err)
            else:
                return self

        raise ValueError(
            "Timing parameters must conform to one of the defined options (A-E).\n"
            "Validation failed for all timing-config options:\n - "
            "\n - ".join(str(err) for err in errors)
        )


class TaskInformation(BaseModel):
    """Behavioral/cognitive task."""

    model_config = ConfigDict(extra="allow", validate_default=True)
    task_name: str = Field(
        ...,
        description="Name of the task. No two tasks should have the same name.",
        alias="TaskName",
    )
    task_description: Annotated[Optional[str], AfterValidator(warn_if_none)] = Field(
        None,
        description="Longer description of the task.",
        alias="TaskDescription",
    )
    cog_atlas_id: Optional[AnyUrl] = Field(
        None,
        description="URI of the corresponding Cognitive Atlas Task term.",
        alias="CogAtlasID",
    )
    cog_po_id: Optional[AnyUrl] = Field(
        None,
        description="URI of the corresponding CogPO term.",
        alias="CogPOID",
    )


class InstitutionInformation(BaseModel):
    """Experiment institution."""

    model_config = ConfigDict(extra="allow", validate_default=True)
    institution_name: Annotated[Optional[str], AfterValidator(warn_if_none)] = Field(
        None,
        description="The name of the institution in charge of the equipment that produced the measurements.",
        alias="InstitutionName",
    )
    institution_address: Annotated[Optional[str], AfterValidator(warn_if_none)] = Field(
        None,
        description="The address of the institution in charge of the equipment that produced the measurements.",
        alias="InstitutionAddress",
    )
    institutional_department_name: Annotated[
        Optional[str], AfterValidator(warn_if_none)
    ] = Field(
        None,
        description="The department in the institution in charge of the equipment that produced the measurements.",
        alias="InstitutionalDepartmentName",
    )


class FUSISidecar(
    InstitutionInformation,
    TaskInformation,
    TimingParameters,
    PowerDopplerIntegration,
    ClutterFiltering,
    SequenceSpecifics,
    Hardware,
):
    """Complete fUSI-BIDS sidecar JSON specification model."""

    model_config = ConfigDict(extra="allow", validate_default=True)
