# -*- coding: utf-8 -*-
"""Tools for converting I3 histograms to plotly Bar graphs."""

from typing import List, Optional, Union

import plotly.graph_objs as go  # type: ignore

# local imports
import maddash_api as api


def _has_all_data(histograms: list) -> bool:
    return any(histograms) and all(histograms)  # deal breakers: empty list, 1+ empty members


def _get_layout(histograms: List[api.Histogram], title: Union[str, None], y_log: bool, alert_no_data: bool, no_title: bool) -> go.Layout:
    """Get the layout for the histogram(s) plot."""
    histograms = list(filter(None, histograms))

    # Title
    if not title:
        if no_title:
            title = None
        elif _has_all_data(histograms):
            title = histograms[0].name
    if y_log and title:
        title = f"{title} (Log)"

    # Margin
    margin = {'l': 30, 'r': 30}
    if not title:  # decrease the top margin, if there's no title
        margin['t'] = 50

    # Y-Axis
    yaxis = None
    if y_log:
        yaxis = {'type': 'log', 'autorange': True}

    # X-Axis
    xaxis = None
    if not _has_all_data(histograms):
        if alert_no_data:
            xaxis = {'title': '(no data)'}

    # Background Color -- gray, if there's no data
    plot_bgcolor = None
    if not _has_all_data(histograms):
        plot_bgcolor = '#E6E6E6'

    return go.Layout(title=title,
                     yaxis=yaxis,
                     xaxis=xaxis,
                     margin=margin,
                     plot_bgcolor=plot_bgcolor)


def _get_data(histograms: List[api.Histogram]) -> Union[List[go.Bar], None]:
    """Get the data for the histogram(s) plot."""
    histograms = list(filter(None, histograms))

    data = None
    if _has_all_data(histograms):
        # Use the name of the collection if all the histograms have the same name
        use_collection_names = len(set(h.name for h in histograms)) == 1

        first = histograms[0]  # Use first histogram for common attributes

        # Data
        bin_width = (first.xmax - first.xmin) / float(len(first.bin_values))
        x_values = [first.xmin + i * bin_width for i in range(len(first.bin_values))]
        text = f"nan({first.nan_count}) under({first.underflow}) over({first.overflow})"

        data = []
        for histo in histograms:
            data.append(go.Bar(x=x_values,
                               y=histo.bin_values,
                               text=text,
                               name=histo.name if not use_collection_names else histo.collection))
    return data


def mdh_to_plotly(histograms: Union[Optional[api.Histogram], List[api.Histogram]], title: str=None, y_log: bool=False, alert_no_data: bool=False, no_title: bool=False) -> go.Figure:
    """Return a plotly Bar graph object with a n overlapped histograms.

    If the contents in `histograms` are not complete, ignore any other data.

    Arguments:
        histograms -- a single api.Histogram or a list of n api.Histogram

    Keyword arguments:
        title -- title of the plot (default: histograms[0]['name'])
        y_log -- change plot's y-axis to logarithmic (default: {False})
        alert_no_data -- add a message below the plot if there is no data (default: {False})
        no_title -- do not add a title to plot (default: {False})

    Raises a {TypeError} `histograms` argument needs to be a single dict or a list of n dicts.
    """
    # make `histograms` a list with no Nones
    if histograms is None:
        histograms = []
    elif isinstance(histograms, api.Histogram):
        histograms = [histograms]

    if not (isinstance(histograms, list) and all(isinstance(h, api.Histogram) for h in histograms)):
        raise TypeError(
            "`histograms` argument needs to be a single api.Histogram or a list of n api.Histogram.")

    layout = _get_layout(histograms, title, y_log, alert_no_data, no_title)
    data = _get_data(histograms)

    return go.Figure(data=data, layout=layout)
