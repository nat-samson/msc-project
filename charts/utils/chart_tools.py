"""This module provides functions for adapting Django queryset data into a format suitable for Chart.JS."""

"""Colours for use with Chart.JS in rgba format. Each is a tuple of (area-colour, border-colour).

e.g. [(area-colour1, border-colour1), (area-colour2, border-colour2)... etc]
"""
DEFAULT_CHART_PALETTE = (
    ('rgba(255, 99, 132, 0.5)', 'rgba(255, 99, 132, 1)'),
    ('rgba(54, 162, 235, 0.5)', 'rgba(54, 162, 235, 1)'),
    ('rgba(255, 206, 86, 0.5)', 'rgba(255, 206, 86, 1)'),
    ('rgba(75, 192, 192, 0.5)', 'rgba(75, 192, 192, 1)'),
    ('rgba(153, 102, 255, 0.5)', 'rgba(153, 102, 255, 1)'),
    ('rgba(255, 159, 64, 0.5)', 'rgba(255, 159, 64, 1)'),
    ('rgba(129, 133, 137, 0.5)', 'rgba(129, 133, 137, 1)'),
    ('rgba(50, 205, 50, 0.5)', 'rgba(50, 205, 50, 1)'),
)


def prepare_data(data, label, override_colours=False):
    """Prepares queryset data for use with Chart.JS by adding chart labels, colours and adapting into dictionary."""
    labels_and_data = _unzip(data)

    if override_colours:
        colours = override_colours
    else:
        colours = _get_colours(len(labels_and_data[0]))

    return _format_for_chart_js(labels_and_data, colours, label)


def _get_colours(count, palette=DEFAULT_CHART_PALETTE):
    """Cycles through the available colours defined above, creating a list matching the length of the dataset."""
    colours = []

    if len(palette) > 0:
        for i in range(count):
            rolling_index = i % len(palette)
            colour = palette[rolling_index]
            colours.append((colour[0], colour[1]))

    return _unzip(colours)


def _unzip(zipped):
    """Unzips the queryset tuples for use with Chart.JS.

    i.e.
    [(x1, y1), (x2, y2) ... (xn, yn)]
    becomes...
    [(x1, x2 ... xn), (y1, y2 ... yn)]
    """
    return list(zip(*zipped))


def _format_for_chart_js(labels_and_data, colours, label):
    """Set up some common chart data for Chart.JS and insert the data derived from the queryset."""
    return {
        "labels": labels_and_data[0],
        "datasets": [{
            "label": label,
            "data": labels_and_data[1],
            "backgroundColor": colours[0],
            "borderColor": colours[1],
            "borderWidth": 2,
            "tension": 0.2,
        }]
    }
