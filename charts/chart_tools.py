# [(area-colour1, border-colour1), (area-colour2, border-colour2)... etc]
CHART_COLOURS = [
    ('rgba(255, 99, 132, 0.2)', 'rgba(255, 99, 132, 1)'),
    ('rgba(54, 162, 235, 0.2)', 'rgba(54, 162, 235, 1)'),
    ('rgba(255, 206, 86, 0.2)', 'rgba(255, 206, 86, 1)'),
    ('rgba(75, 192, 192, 0.2)', 'rgba(75, 192, 192, 1)'),
    ('rgba(153, 102, 255, 0.2)', 'rgba(153, 102, 255, 1)'),
    ('rgba(255, 159, 64, 0.2)', 'rgba(255, 159, 64, 1)'),
]


def get_colours(count):
    # cycle through the available colours in the palette
    colours = []

    if len(CHART_COLOURS) > 0:
        for i in range(count):
            rolling_index = i % len(CHART_COLOURS)
            colour = CHART_COLOURS[rolling_index]
            colours.append((colour[0], colour[1]))

    return unzip(colours)


def unzip(zipped):
    # takes QuerySet tuples: [(x1, y1), (x2, y2) ... (xn, yn)]
    # returns [(x1, x2 ... xn), (y1, y2 ... yn)]
    return list(zip(*zipped))
