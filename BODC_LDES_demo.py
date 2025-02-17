# python test file that will do sparql query to an endpoint of BODC

import requests
import urllib.parse
import json
import time
import sys
import os
import datetime
from sema.query import QueryResult, DefaultSparqlBuilder, GraphSource as KGSource
from pandas import DataFrame
from sema.subyt import (
    Generator,
    GeneratorSettings,
    Sink,
    Source,
    SinkFactory,
    SourceFactory,
    JinjaBasedGenerator,
)

# define variables
collections = ["P02"]
begin_date = "2012-01-01 00:00:00"
end_date = "2021-01-02 00:00:00"
retention_period = 100

# define constants
ENDPOINT = "http://vocab.nerc.ac.uk/sparql/sparql"
PYKG2TBL_OUTPUT_FOLDER = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "output_pykg2tbl"
)
PYSUBYT_OUTPUT_FOLDER = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "output_pysubyt"
)
KGSOURCE = KGSource.build(ENDPOINT)
TEMPLATES_FOLDER_PYKG2TBL = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "pykg2tbl"
)
TEMPLATES_FOLDER_PYSUBYT = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "pysubyt"
)
GENERATOR = DefaultSparqlBuilder(templates_folder=TEMPLATES_FOLDER_PYKG2TBL)

# demo url http://vocab.nerc.ac.uk/sparql/sparql?query={YOUR_QUERY_URL_ENCODED}


def generate_sparql(name: str, **vars):
    """
    Generate a SPARQL query from a template
    """
    return GENERATOR.build_syntax(name, **vars)


def execute_to_df(name: str, **vars) -> DataFrame:
    """Builds the sparql and executes, returning the result as a dataframe."""
    sparql = generate_sparql(name, **vars)
    print(sparql)
    result: QueryResult = KGSOURCE.query(sparql)
    return result.to_dataframe()


def make_json(DATAFRAME):
    # convert dataframe to json
    json_records = DATAFRAME.to_json(orient="records")
    # format the json
    json_records = json.loads(json_records)
    # print(json_records)
    return json_records


def save_json(json_records, collection, begin_date, end_date):
    name = collection + "_" + begin_date + "_" + end_date + ".json"
    # make sure the name is safe to write to file
    name = name.replace(":", "-")
    name = name.replace("-", "_")
    name = name.replace(" ", "_")

    # save json to file
    with open(os.path.join(PYKG2TBL_OUTPUT_FOLDER, name), "w") as outfile:
        json.dump(json_records, outfile)
    return os.path.join(PYKG2TBL_OUTPUT_FOLDER, name)


def make_pykg2tbl_files(collections, begin_date, end_date):
    # for each collection
    for collection in collections:
        # devide the time period into 1 year
        # for each year
        first = True
        for year in range(int(begin_date[:4]), int(end_date[:4]) + 1):
            # make the begin and end date for the year
            begin_date_year = str(year) + "-01-01 00:00:00"
            end_date_year = str(year) + "-12-31 00:00:00"
            prev_year = year - 1

            this_delta = (
                str(year) + "-01-01 00:00:00" + "_" + str(year) + "-12-31 00:00:00"
            )
            this_delta_quoted = urllib.parse.quote(this_delta)
            next_delta_quoted = ""
            if not first:
                next_delta = (
                    str(prev_year)
                    + "-12-31 00:00:00"
                    + "_"
                    + str(year)
                    + "-01-01 00:00:00"
                )
                next_delta_quoted = urllib.parse.quote(next_delta)
            if first:
                first = False

            # check if end date is greater than the end date of the time period
            if year == int(end_date[:4]):
                end_date_year = end_date

            # check if begin date is less than the begin date of the time period
            if year == int(begin_date[:4]):
                begin_date_year = begin_date
            # make the sparql query
            DATAFRAME = execute_to_df(
                "collection-changes-between-delta-period.sparql",
                collection=collection,
                date1=begin_date_year,
                date2=end_date_year,
            )
            print(DATAFRAME)
            # convert dataframe to json
            json_records = make_json(DATAFRAME)
            # save json to file
            json_file_loc = save_json(
                json_records, collection, begin_date_year, end_date_year
            )

            begin_delta = datetime.datetime.strptime(
                begin_date_year, "%Y-%m-%d %H:%M:%S"
            )

            name_ttl = collection + "_" + begin_date + "_" + end_date + ".ttl"
            formatted_name = this_delta.replace(":", "-")
            formatted_name = formatted_name.replace("-", "_")
            formatted_name = formatted_name.replace(" ", "_")
            formatted_name = collection + "_" + formatted_name + ".ttl"
            output_file = os.path.join(PYSUBYT_OUTPUT_FOLDER, formatted_name)

            # make vars dict
            vars_dict = {
                "this_fragment_delta": this_delta_quoted,
                "next_fragment_delta": next_delta_quoted,
                "next_fragment_time": end_date_year.replace(" ", "T") + "Z",
                "retention_period": retention_period,
                "collection": collection,
            }

            # make service and sink
            service = JinjaBasedGenerator(TEMPLATES_FOLDER_PYSUBYT)
            sink = SinkFactory.make_sink(
                os.path.join(PYSUBYT_OUTPUT_FOLDER, output_file), False
            )
            inputs = {"qres": SourceFactory.make_source(json_file_loc)}
            settings = GeneratorSettings()
            service.process("ldes_fragment.ttl", inputs, settings, sink, vars_dict)
            time.sleep(1)


make_pykg2tbl_files(collections, begin_date, end_date)
