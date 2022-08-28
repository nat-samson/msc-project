# [(area-colour1, border-colour1), (area-colour2, border-colour2)... etc]
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


def get_colours(count, palette=DEFAULT_CHART_PALETTE):
    # cycle through the available colours in the palette
    colours = []

    if len(palette) > 0:
        for i in range(count):
            rolling_index = i % len(palette)
            colour = palette[rolling_index]
            colours.append((colour[0], colour[1]))

    return unzip(colours)


def unzip(zipped):
    # takes QuerySet tuples: [(x1, y1), (x2, y2) ... (xn, yn)]
    # returns [(x1, x2 ... xn), (y1, y2 ... yn)]
    return list(zip(*zipped))
