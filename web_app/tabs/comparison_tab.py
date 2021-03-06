"""Dash tab for comparing histograms."""

from typing import Dict, List

import dash_core_components as dcc  # type: ignore
import dash_daq as daq  # type: ignore
import dash_html_components as html  # type: ignore
import plotly.graph_objs as go  # type: ignore
from dash.dependencies import Input, Output  # type: ignore

from ..config import app
from ..styles import CENTERED_100, SHORT_HR, WIDTH_45
from ..utils import db
from ..utils import histogram_converter as hc
from .database_controls import get_database_name_options, get_default_database


def layout() -> html.Div:
    """Construct the HTML."""
    return html.Div(
        children=[
            html.Div(
                style=WIDTH_45,
                children=[
                    html.H6("Database"),
                    dcc.Dropdown(
                        id="database-name-dropdown-tab2",
                        value=get_default_database(),
                        options=get_database_name_options(),
                    ),
                ],
            ),
            ####
            html.Hr(),
            ####
            html.Div(
                children=[
                    html.H6("Collections"),
                    dcc.Dropdown(id="collections-dropdown-tab2", multi=True),
                ]
            ),
            ####
            html.Hr(),
            ####
            html.Div(
                children=[
                    html.H3("Histogram Comparisons"),
                    html.Div(
                        style=CENTERED_100,
                        children=[
                            html.Div(
                                style=WIDTH_45,
                                children=[dcc.Dropdown(id="histogram-dropdown-tab2")],
                            )
                        ],
                    ),
                    html.Div(
                        className="row",
                        style=CENTERED_100,
                        children=[
                            html.Div(dcc.Graph(id="plot-histogram-tab2")),
                            daq.BooleanSwitch(  # pylint: disable=E1101
                                id="toggle-log-tab2", on=False, label="log"
                            ),
                        ],
                    ),
                    ####
                    html.Hr(style=SHORT_HR),
                    ####
                    html.Div(
                        className="row",
                        children=[
                            html.Div(
                                className="two columns",
                                style=WIDTH_45,
                                children=[dcc.Graph(id="plot-histogram-ratio-tab2")],
                            ),
                            html.Div(
                                className="two columns",
                                style=WIDTH_45,
                                children=[dcc.Graph(id="plot-histogram-cdf-tab2")],
                            ),
                        ],
                    ),
                ]
            ),
            ####
            html.Hr(),
            ####
            html.Table(id="collection-comparison-result-tab2"),
        ]
    )


# --------------------------------------------------------------------------------------------------
# Collections


@app.callback(
    Output("collections-dropdown-tab2", "options"),
    [Input("database-name-dropdown-tab2", "value")],
)  # type: ignore
def set_collection_options(database_name: str) -> List[Dict[str, str]]:
    """Return the list of collections for the dropdown menu."""
    collection_names = db.get_collection_names(database_name)

    return [{"label": name, "value": name} for name in collection_names]


# --------------------------------------------------------------------------------------------------
# Histograms


@app.callback(
    Output("histogram-dropdown-tab2", "options"),
    [
        Input("database-name-dropdown-tab2", "value"),
        Input("collections-dropdown-tab2", "value"),
    ],
)  # type: ignore
def update_histogram_dropdown_options(
    database_name: str, collection_names: List[str]
) -> List[Dict[str, str]]:
    """Return the collections' mutual list of histograms for dropdown menu."""
    if not collection_names:
        return []

    all_histogram_names = [
        db.get_histogram_names(c, database_name) for c in collection_names
    ]

    # get common histogram names
    sets_of_names = [set(names) for names in all_histogram_names]
    if not any(sets_of_names):
        return []
    histogram_names = sorted(set.intersection(*sets_of_names))

    return [{"label": name, "value": name} for name in histogram_names]


@app.callback(
    Output("plot-histogram-tab2", "figure"),
    [
        Input("histogram-dropdown-tab2", "value"),
        Input("histogram-dropdown-tab2", "options"),
        Input("toggle-log-tab2", "on"),
        Input("database-name-dropdown-tab2", "value"),
        Input("collections-dropdown-tab2", "value"),
    ],
)  # type: ignore
def update_histogram(
    histogram_name: str,
    histogram_options: List[str],
    log: bool,
    database_name: str,
    collection_names: List[str],
) -> go.Figure:
    """Plot each collection's histograms on the same plot."""
    if not collection_names or not histogram_options:
        return hc.i3histogram_to_plotly(None, y_log=log, no_title=True)

    all_histograms = [
        db.get_histogram(histogram_name, c, database_name) for c in collection_names
    ]

    return hc.i3histogram_to_plotly(
        list(filter(None, all_histograms)), y_log=log, no_title=True
    )


# --------------------------------------------------------------------------------------------------
# Comparison Table


@app.callback(
    Output("collection-comparison-result-tab2", "children"),
    [
        Input("database-name-dropdown-tab2", "value"),
        Input("collections-dropdown-tab2", "value"),
    ],
)  # type: ignore
def compare_collections(
    database_name: str, collection_names: List[str]
) -> List[html.Tr]:
    """TODO."""
    if not collection_names:
        return []

    print("compare_collections: Comparing...")
    headers = ["Histogram", "Chi2", "KS", "AD", "Result", "Notes"]
    table_elements = [html.Tr([html.Th(h) for h in headers])]

    # def extract_histograms(database_name: str, collection_name: str) -> Dict[str, str]:
    #     histograms = db.get_histograms(collection_name, database_name)
    #     return {h['name']: h for h in histograms} if histograms else {}

    # lhs_histograms = extract_histograms(database_name, collection_names[0])
    # rhs_histograms = extract_histograms(database_name, collection_names[1])

    # results = {}
    # for lhs_name, lhs_histogram in lhs_histograms.items():
    #     if lhs_name not in rhs_histograms:
    #         print("Histogram %s in LHS, but not RHS." % lhs_name)
    #         continue
    #     rhs_histogram = rhs_histograms[lhs_name]
    #     results[lhs_name] = compare(lhs_histogram, rhs_histogram)

    # headers = ['Histogram', 'Chi2', 'KS', 'AD', 'Result', 'Notes']
    # table_elements = [html.Tr([html.Th(h) for h in headers])]
    # for name, result in results.items():
    #     chi2_result = result['chisq']['pvalue'] if 'chisq' in result else '---'
    #     KS_result = result['KS']['pvalue'] if 'KS' in result else '---'
    #     AD_result = result['AD']['pvalue'] if 'AD' in result else '---'
    #     pass_fail = 'PASS'
    #     notes = 'N/A'

    #     if 'chisq' not in result and 'KS' not in result and 'AD' not in result:
    #         if len(result) == 1:
    #             notes = list(result.keys())[0]

    #     row_data = [name, str(chi2_result), KS_result, AD_result, pass_fail, notes]
    #     row = html.Tr([html.Td(d) for d in row_data])
    #     table_elements.append(row)

    print("compare_collections: Done.")
    return table_elements
