# <snippet name="docs/docusaurus/docs/core/connect_to_data/filesystem_data/_create_a_data_asset/_s3/_directory_asset.py - full example">
# <snippet name="docs/docusaurus/docs/core/connect_to_data/filesystem_data/_create_a_data_asset/_s3/_directory_asset.py - retrieve Data Source">
import great_expectations as gx

# This example uses a File Data Context which already has
#  a Data Source defined.
context = gx.get_context()
data_source_name = "my_filesystem_data_source"
data_source = context.get_datasource(data_source_name)
# </snippet>

# Define the Data Asset's parameters:
# <snippet name="docs/docusaurus/docs/core/connect_to_data/filesystem_data/_create_a_data_asset/_s3/_directory_asset.py - define Data Asset parameters">
asset_name = "s3_taxi_csv_directory_asset"
s3_prefix = "data/taxi_yellow_tripdata_samples/"
data_directory = "data/taxi_yellow_tripdata_samples/"
# </snippet>

# Add the Data Asset to the Data Source:
# <snippet name="docs/docusaurus/docs/core/connect_to_data/filesystem_data/_create_a_data_asset/_s3/_directory_asset.py - add Data Asset">
s3_file_data_asset = data_source.add_directory_csv_asset(
    name=asset_name, s3_prefix=s3_prefix, data_directory=data_directory
)
# </snippet>
# </snippet>