from django.test import SimpleTestCase

from charts.utils import chart_tools
from charts.utils.chart_tools import _unzip, _get_colours


class ChartToolsTests(SimpleTestCase):
    def test_unzip_good_input(self):
        zipped_data = [(1, "a"), (2, "b"), (3, "c")]
        expected = [(1, 2, 3), ("a", "b", "c")]
        actual = _unzip(zipped_data)
        self.assertEquals(expected, actual)

    def test_unzip_single_tuple(self):
        zipped_data = [(1, "a")]
        expected = [(1,), ("a",)]
        actual = _unzip(zipped_data)
        self.assertEquals(expected, actual)

    def test_unzip_empty(self):
        empty_zip = []
        expected = []
        actual = _unzip(empty_zip)
        self.assertEquals(expected, actual)

    def test_get_zero_colours(self):
        expected = []
        actual = _get_colours(0)
        self.assertEquals(expected, actual)

    def test_cycle_through_colours(self):
        # get more colours than there are presets
        n = len(chart_tools.DEFAULT_CHART_PALETTE)
        colours = _get_colours(5 * n)

        # the nth colour should be identical to the 2*nth, 3*nth etc.
        n_colour = colours[0][n]
        n2_colour = colours[0][n * 2]
        n3_colour = colours[0][n * 3]
        n_plus_1_colour = colours[0][n + 1]
        n2_plus_1_colour = colours[0][2 * n + 1]
        self.assertEquals(n_colour, n2_colour)
        self.assertEquals(n_colour, n3_colour)
        self.assertEquals(n_plus_1_colour, n2_plus_1_colour)

    def test_get_colours_when_no_presets(self):
        empty_preset_palette = []
        actual = _get_colours(5, empty_preset_palette)
        expected = []
        self.assertEquals(expected, actual)
