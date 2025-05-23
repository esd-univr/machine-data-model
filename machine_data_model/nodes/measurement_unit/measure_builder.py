import inspect
from enum import Enum
from typing import Type, Dict

import unitsnet_py
from unitsnet_py.abstract_unit import AbstractMeasure


class NoneMeasureUnits(Enum):
    """
    Enum for representing units for `NoneMeasure`.

    :cvar NONE: The only available unit, representing no unit.
    """

    NONE = 0


class NoneMeasure(AbstractMeasure):
    """
    Represents a value with no unit.

    This class is used to represent a value that does not have any unit
    associated with it. The unit of measurement is always `NONE`.

    :ivar _value: The value.
    """

    def __init__(
        self, value: float, from_unit: NoneMeasureUnits = NoneMeasureUnits.NONE
    ):
        """
        Initializes a `NoneMeasure` instance with a value and a unit.

        :param value: The value of the `NoneMeasure`.
        :param from_unit: The unit of the value. This is always `NONE`, and an assertion ensures it cannot be anything else.
        """

        assert from_unit == NoneMeasureUnits.NONE
        self._value: float = value

    @property
    def base_value(self) -> float:
        """
        Returns the base value.

        :return: The value with no unit.
        """

        return self._value

    def to_string(
        self,
        unit: NoneMeasureUnits = NoneMeasureUnits.NONE,
        fractional_digits: int | None = None,
    ) -> str:
        """
        Format the `NoneMeasure` to a string.

        This method returns the string representation of the value. The unit is
        always `NONE`, and an optional number of fractional digits can be
        specified.

        :param unit: The unit to format the `NoneMeasure`. The only valid value is `NONE`.
        :param fractional_digits: The number of fractional digits to keep. Optional.
        :return: A string representation of the `NoneMeasure`.
        """

        assert unit == NoneMeasureUnits.NONE
        if fractional_digits is not None:
            return (
                f"{super()._truncate_fraction_digits(self._value, fractional_digits)}"
            )
        return f"{self._value}"

    def get_unit_abbreviation(
        self, unit_abbreviation: NoneMeasureUnits = NoneMeasureUnits.NONE
    ) -> str:
        """
        Get the abbreviation of the `NoneMeasure` unit.

        This method returns an empty string since the only valid unit is `NONE`.

        :param unit_abbreviation: The unit abbreviation. Must be `NONE`.
        :return: An empty string as `NoneMeasure` has no abbreviation.

        :raises ValueError: If the unit is not `NONE`.
        """

        if unit_abbreviation == NoneMeasureUnits.NONE:
            return ""
        else:
            raise ValueError("Invalid unit for NoneMeasure measure")


class MeasureBuilder:
    """
    A utility class for building measure objects from a value and a unit.

    This class helps in creating an appropriate measure object, such as
    `NoneMeasure` or units from the `unitsnet_py` package, based on the provided
    unit.

    :ivar _measure_ctor: A dictionary that maps unit classes to their corresponding measure constructors.
    """

    def __init__(self) -> None:
        """
        Initializes a new `MeasureBuilder` instance.

        This constructor dynamically loads unit classes from the `unitsnet_py`
        package, mapping each unit class to its corresponding measure class, and
        sets up the `_measure_ctor` dictionary for quick lookup.
        """

        self._measure_ctor: Dict[Type[Enum], Type[AbstractMeasure]] = {}

        # Explore the unitsnet_py package to store the measure object from the unit.
        units = inspect.getmembers(
            unitsnet_py,
            lambda member: inspect.isclass(member)
            and member.__name__.endswith("Units"),
        )
        for unit in units:
            unit_name = unit[0]
            measure_name = unit_name.replace("Units", "")
            measure = getattr(unitsnet_py, measure_name)
            assert inspect.isclass(measure)
            self._measure_ctor[unit[1]] = measure

        # Add the NoneMeasure unit.
        self._measure_ctor[NoneMeasureUnits] = NoneMeasure

    def get_measure_unit(self, unit: str | Enum) -> Enum:
        """
        Retrieves the unit class based on the given unit name or unit enum.

        If a string is passed, it is expected to be in the format "Module.Unit".
        If an enum is passed, the corresponding unit is returned.

        :param unit: The unit, either as a string (e.g., "LengthUnits.Meter") or an `Enum`.
        :return: The unit class corresponding to the provided unit.

        :raises ValueError: If the unit type is invalid.
        """

        if isinstance(unit, Enum):
            assert unit.__class__ in self._measure_ctor
            return unit
        elif isinstance(unit, str):
            assert "." in unit
            unit_class, unit_name = unit.split(".")
        else:
            raise ValueError("Invalid unit type")

        if unit_class == "NoneMeasureUnits":
            unit_cl = NoneMeasureUnits
        else:
            unit_cl = getattr(unitsnet_py, unit_class)
        return unit_cl[unit_name]

    def create_measure(self, value: float, unit: str | Enum) -> AbstractMeasure:
        """
        Creates a measure object using the provided value and unit.

        This method looks up the correct measure constructor from
        `_measure_ctor` and creates an instance of the appropriate measure class
        with the specified value and unit.

        :param value: The value of the measure.
        :param unit: The unit of the measure, provided as a string (e.g., "LengthUnits.Meter") or an `Enum` representing the unit.
        :return: An instance of the corresponding measure class (e.g., `NoneMeasure` or a unit from `unitsnet_py`).

        :raises ValueError: If the unit is invalid or cannot be matched to a known unit.
        """

        unit = self.get_measure_unit(unit)
        measure = self._measure_ctor[unit.__class__]
        return measure(value=value, from_unit=unit)


_measure_builder: "MeasureBuilder" = MeasureBuilder()


def get_measure_builder() -> "MeasureBuilder":
    """
    Get the MeasureBuilder instance.

    :return: The MeasureBuilder instance.
    """
    return _measure_builder
