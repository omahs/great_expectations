import us

from great_expectations.execution_engine import PandasExecutionEngine
from great_expectations.expectations.expectation import ColumnMapExpectation
from great_expectations.expectations.metrics import (
    ColumnMapMetricProvider,
    column_condition_partial,
)


def is_valid_state_or_territory(state: str, dc_statehood: bool):
    list_of_states_and_territories = [str(x) for x in us.states.STATES_AND_TERRITORIES]
    if dc_statehood is True:
        list_of_states_and_territories.append("District Of Columbia")
    else:
        pass
    if len(state) > 24 or type(state) != str:  # noqa: E721
        return False
    return state in list_of_states_and_territories


# This class defines a Metric to support your Expectation.
# For most ColumnMapExpectations, the main business logic for calculation will live in this class.
class ColumnValuesToBeValidUSState(ColumnMapMetricProvider):
    # This is the id string that will be used to reference your metric.
    condition_metric_name = "column_values.valid_us_state_or_territory"

    # This method implements the core logic for the PandasExecutionEngine
    @column_condition_partial(engine=PandasExecutionEngine)
    def _pandas(cls, column, dc_statehood=True, **kwargs):
        return column.apply(lambda x: is_valid_state_or_territory(x, dc_statehood))

    # This method defines the business logic for evaluating your metric when using a SqlAlchemyExecutionEngine
    # @column_condition_partial(engine=SqlAlchemyExecutionEngine)
    # def _sqlalchemy(cls, column, _dialect, **kwargs):
    #     raise NotImplementedError

    # This method defines the business logic for evaluating your metric when using a SparkDFExecutionEngine
    # @column_condition_partial(engine=SparkDFExecutionEngine)
    # def _spark(cls, column, **kwargs):
    #     raise NotImplementedError


# This class defines the Expectation itself
class ExpectColumnValuesToBeValidUSStateOrTerritory(ColumnMapExpectation):
    """Expect values in this column to be valid state abbreviations.
    See https://pypi.org/project/us/ for more information.
    DC statehood is a perennial issue in data science, and the owners of the us repo addressed it differently than we have: https://github.com/unitedstates/python-us/issues/50
    dc_statehood defaults to True, though can be overriden by end users
    """

    # These examples will be shown in the public gallery.
    # They will also be executed as unit tests for your Expectation.
    examples = [
        {
            "data": {
                "valid_state_or_territory": [
                    "American Samoa",
                    "Virgin Islands",
                    "Guam",
                    "Northern Mariana Islands",
                    "Puerto Rico",
                    "Kansas",
                ],
                "invalid_state_or_territory": [
                    "",
                    "1234",
                    "Weet Virginia",
                    "Kansass",
                    "123 Hawaii",
                    "Southern Mariana Islands",
                ],
            },
            "tests": [
                {
                    "title": "basic_positive_test",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "valid_state_or_territory"},
                    "out": {"success": True},
                },
                {
                    "title": "basic_negative_test",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "invalid_state_or_territory"},
                    "out": {"success": False},
                },
            ],
        }
    ]

    # This is the id string of the Metric used by this Expectation.
    # For most Expectations, it will be the same as the `condition_metric_name` defined in your Metric class above.
    map_metric = "column_values.valid_us_state_or_territory"

    # This is a list of parameter names that can affect whether the Expectation evaluates to True or False
    success_keys = ("mostly",)

    # This dictionary contains default values for any parameters that should have default values
    default_kwarg_values = {}

    # This object contains metadata for display in the public Gallery
    library_metadata = {
        "maturity": "experimental",  # "experimental", "beta", or "production"
        "tags": [
            "hackathon",
            "typed-entities",
        ],  # Tags for this Expectation in the Gallery
        "contributors": [  # Github handles for all contributors to this Expectation.
            "@luismdiaz01",
            "@derekma73",  # Don't forget to add your github handle here!
        ],
        "requirements": ["us"],
    }


if __name__ == "__main__":
    ExpectColumnValuesToBeValidUSStateOrTerritory().print_diagnostic_checklist()
