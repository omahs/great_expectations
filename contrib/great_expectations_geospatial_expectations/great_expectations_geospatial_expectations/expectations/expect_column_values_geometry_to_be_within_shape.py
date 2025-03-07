import pandas as pd
import pygeos as geos

from great_expectations.execution_engine import PandasExecutionEngine
from great_expectations.expectations.expectation import ColumnMapExpectation
from great_expectations.expectations.metrics import (
    ColumnMapMetricProvider,
    column_condition_partial,
)


# This class defines a Metric to support your Expectation.
# For most ColumnMapExpectations, the main business logic for calculation will live in this class.
class ColumnValuesGeometryWithinShape(ColumnMapMetricProvider):
    # This is the id string that will be used to reference your metric.
    condition_metric_name = "column_values.geometry.within_shape"
    condition_value_keys = ("shape", "shape_format", "column_shape_format", "properly")

    # This method implements the core logic for the PandasExecutionEngine
    @column_condition_partial(engine=PandasExecutionEngine)
    def _pandas(cls, column, **kwargs):  # noqa: C901 - too complex
        shape = kwargs.get("shape")
        shape_format = kwargs.get("shape_format")
        column_shape_format = kwargs.get("column_shape_format")
        properly = kwargs.get("properly")

        # Check that shape is given and given in the correct format
        if shape is not None:
            try:
                if shape_format == "wkt":
                    shape_ref = geos.from_wkt(shape)
                elif shape_format == "wkb":
                    shape_ref = geos.from_wkb(shape)
                elif shape_format == "geojson":
                    shape_ref = geos.from_geojson(shape)
                else:
                    raise NotImplementedError(  # noqa: TRY301
                        "Shape constructor method not implemented. Must be in WKT, WKB, or GeoJSON format."
                    )
            except Exception:
                raise Exception("A valid reference shape was not given.")  # noqa: TRY002, TRY003
        else:
            raise Exception("A shape must be provided for this method.")  # noqa: TRY002, TRY003

        # Load the column into a pygeos Geometry vector from numpy array (Series not supported).
        if column_shape_format == "wkt":
            shape_test = geos.from_wkt(column.to_numpy(), on_invalid="ignore")
        elif column_shape_format == "wkb":
            shape_test = geos.from_wkb(column.to_numpy(), on_invalid="ignore")
        else:
            raise NotImplementedError("Column values shape format not implemented.")

        # Allow for an array of reference shapes to be provided. Return a union of all the shapes in the array (Polygon or Multipolygon)
        shape_ref = geos.union_all(shape_ref)

        # Prepare the geometries
        geos.prepare(shape_ref)
        geos.prepare(shape_test)

        if properly:
            return pd.Series(geos.contains_properly(shape_ref, shape_test))
        else:
            return pd.Series(geos.contains(shape_ref, shape_test))

    # This method defines the business logic for evaluating your metric when using a SqlAlchemyExecutionEngine
    # @column_condition_partial(engine=SqlAlchemyExecutionEngine)
    # def _sqlalchemy(cls, column, _dialect, **kwargs):
    #     raise NotImplementedError

    # This method defines the business logic for evaluating your metric when using a SparkDFExecutionEngine
    # @column_condition_partial(engine=SparkDFExecutionEngine)
    # def _spark(cls, column, **kwargs):
    #     raise NotImplementedError


# This class defines the Expectation itself
class ExpectColumnValuesGeometryToBeWithinShape(ColumnMapExpectation):
    """Expect that column values as geometries are within a given reference shape.

    expect_column_values_geometry_to_be_within_shape is a \
    [Column Map Expectation](https://docs.greatexpectations.io/docs/guides/expectations/creating_custom_expectations/how_to_create_custom_column_map_expectations).

    Args:
        column (str): \
            The column name. \
            Column values must be provided in WKT or WKB format, which are commom formats for GIS Database formats. \
            WKT can be accessed thhrough the ST_AsText() or ST_AsBinary() functions in queries for PostGIS and MSSQL.

    Keyword Args:
        shape (str or list of str): \
            The reference geometry
        shape_format (str): \
            Geometry format for 'shape' string(s). Can be provided as 'Well Known Text' (WKT), 'Well Known Binary' (WKB), or as GeoJSON. \
            Must be one of: [wkt, wkb, geojson]. Default: wkt
        column_shape_format (str): \
            Geometry format for 'column'. Column values must be provided in WKT or WKB format, which are commom formats for GIS Database formats. \
            WKT can be accessed thhrough the ST_AsText() or ST_AsBinary() functions in queries for PostGIS and MSSQL.
        properly (boolean): \
            Whether the 'column' values should be properly within in the reference 'shape'. \
            The method allows for shapes to be 'properly contained' within the reference, meaning no points of a given geometry can touch the boundary of the reference. \
            See the pygeos docs for reference. Default: False

    Returns:
        An [ExpectationSuiteValidationResult](https://docs.greatexpectations.io/docs/terms/validation_result)

    Notes:
        * Convention is (X Y Z) for points, which would map to (Longitude Latitude Elevation) for geospatial cases.
        * Any convention can be followed as long as the test and reference shapes are consistent.
        * The reference shape allows for an array, but will union (merge) all the shapes into 1 and check the contains condition.
    """

    # These examples will be shown in the public gallery.
    # They will also be executed as unit tests for your Expectation.
    examples = [
        {
            "data": {
                "points_only": [
                    "POINT(1 1)",
                    "POINT(2 2)",
                    "POINT(6 4)",
                    "POINT(3 9)",
                    "POINT(8 9.999)",
                ],
                "points_and_lines": [
                    "POINT(1 1)",
                    "POINT(2 2)",
                    "POINT(6 4)",
                    "POINT(3 9)",
                    "LINESTRING(5 5, 8 10)",
                ],
            },
            "tests": [
                {
                    "title": "positive_test_with_points",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {
                        "column": "points_only",
                        "shape": "POLYGON ((0 0, 0 10, 10 10, 10 0, 0 0))",
                        "shape_format": "wkt",
                        "properly": False,
                    },
                    "out": {
                        "success": True,
                    },
                },
                {
                    "title": "positive_test_with_points_and_lines",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {
                        "column": "points_and_lines",
                        "shape": "POLYGON ((0 0, 0 10, 10 10, 10 0, 0 0))",
                        "shape_format": "wkt",
                        "properly": False,
                    },
                    "out": {
                        "success": True,
                    },
                },
                {
                    "title": "positive_test_with_points_wkb_reference_shape",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {
                        "column": "points_only",
                        "shape": "010300000001000000050000000000000000000000000000000000000000000000000000000000000000002440000000000000244000000000000024400000000000002440000000000000000000000000000000000000000000000000",
                        "shape_format": "wkb",
                        "properly": False,
                    },
                    "out": {
                        "success": True,
                    },
                },
                {
                    "title": "positive_test_with_points_geojson_reference_shape",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {
                        "column": "points_only",
                        "shape": '{"type":"Polygon","coordinates":[[[0.0,0.0],[0.0,10.0],[10.0,10.0],[10.0,0.0],[0.0,0.0]]]}',
                        "shape_format": "geojson",
                        "properly": False,
                    },
                    "out": {
                        "success": True,
                    },
                },
                {
                    "title": "negative_test_with_points",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {
                        "column": "points_only",
                        "shape": "POLYGON ((0 0, 0 7.5, 7.5 7.5, 7.5 0, 0 0))",
                        "shape_format": "wkt",
                        "properly": True,
                    },
                    "out": {
                        "success": False,
                    },
                },
                {
                    "title": "negative_test_with_points_and_lines_not_properly_contained",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {
                        "column": "points_and_lines",
                        "shape": "POLYGON ((0 0, 0 10, 10 10, 10 0, 0 0))",
                        "shape_format": "wkt",
                        "properly": True,
                        "mostly": 1,
                    },
                    "out": {
                        "success": False,
                    },
                },
            ],
        }
    ]

    # This is the id string of the Metric used by this Expectation.
    # For most Expectations, it will be the same as the `condition_metric_name` defined in your Metric class above.
    map_metric = "column_values.geometry.within_shape"

    # This is a list of parameter names that can affect whether the Expectation evaluates to True or False
    success_keys = (
        "mostly",
        "shape",
        "shape_format",
        "column_shape_format",
        "properly",
    )

    # This dictionary contains default values for any parameters that should have default values
    default_kwarg_values = {
        "mostly": 1,
        "shape_format": "wkt",
        "column_shape_format": "wkt",
        "properly": False,
    }

    # This object contains metadata for display in the public Gallery
    library_metadata = {
        "tags": [
            "geospatial",
            "hackathon-2022",
        ],  # Tags for this Expectation in the Gallery
        "contributors": [  # Github handles for all contributors to this Expectation.
            "@pjdobson",  # Don't forget to add your github handle here!
        ],
        "requirements": ["pygeos"],
    }


if __name__ == "__main__":
    ExpectColumnValuesGeometryToBeWithinShape().print_diagnostic_checklist()
