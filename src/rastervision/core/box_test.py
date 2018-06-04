import unittest

import numpy as np

from rastervision.core.box import Box
from shapely.geometry import box as ShapelyBox

np.random.seed(1)


class TestBox(unittest.TestCase):
    def setUp(self):
        self.ymin = 0
        self.xmin = 0
        self.ymax = 2
        self.xmax = 3
        self.box = Box(self.ymin, self.xmin, self.ymax, self.xmax)
        self.tuple_box = (self.ymin, self.xmin, self.ymax, self.xmax)

    def test_get_height(self):
        height = self.ymax - self.ymin
        self.assertEqual(self.box.get_height(), height)

    def test_get_width(self):
        width = self.xmax - self.xmin
        self.assertEqual(self.box.get_width(), width)

    def test_get_area(self):
        area = self.box.get_height() * self.box.get_width()
        self.assertEqual(self.box.get_area(), area)

    def test_rasterio_format(self):
        rasterio_box = ((self.ymin, self.ymax), (self.xmin, self.xmax))
        self.assertEqual(self.box.rasterio_format(), rasterio_box)

    def test_tuple_format(self):
        self.assertEqual(self.box.tuple_format(), self.tuple_box)

    def test_shapely_format(self):
        shapely_box = (self.xmin, self.ymin, self.xmax, self.ymax)
        self.assertEqual(self.box.shapely_format(), shapely_box)

    def test_npbox_format(self):
        self.assertEqual(tuple(self.box.npbox_format()), self.tuple_box)
        self.assertEqual(self.box.npbox_format().dtype, np.float)

    def test_geojson_coordinates(self):
        nw = (self.xmin, self.ymin)
        ne = (self.xmin, self.ymax)
        se = (self.xmax, self.ymax)
        sw = (self.xmax, self.ymin)
        geojson_coords = [nw, ne, se, sw, nw]
        self.assertEqual(self.box.geojson_coordinates(), geojson_coords)

    def check_random_square(self, box, xlimit, ylimit, size):
        self.assertTrue(box.get_width() == box.get_height())
        self.assertEqual(box.get_width(), size)
        self.assertLessEqual(box.xmax, xlimit)
        self.assertLessEqual(box.ymax, ylimit)
        self.assertGreaterEqual(box.xmin, 0)
        self.assertGreaterEqual(box.ymin, 0)

    def test_make_random_square_container(self):
        xlimit = 10
        ylimit = 10
        size = 5
        nb_tests = 10
        for _ in range(nb_tests):
            container = self.box.make_random_square_container(
                xlimit, ylimit, size)
            self.check_random_square(container, xlimit, ylimit, size)
            self.assertTrue(container.get_shapely().contains(
                self.box.get_shapely()))

    def test_make_random_square(self):
        xlimit = 10
        ylimit = 10
        window = Box(0, 0, xlimit, ylimit)
        size = 5
        nb_tests = 10
        for _ in range(nb_tests):
            box = window.make_random_square(size)
            self.check_random_square(box, xlimit, ylimit, size)

    def test_from_npbox(self):
        npbox = np.array([self.ymin, self.xmin, self.ymax, self.xmax])
        box = Box.from_npbox(npbox)
        self.assertEqual(box.tuple_format(), self.tuple_box)

    def test_from_shapely(self):
        shape = ShapelyBox(self.xmin, self.ymin, self.xmax, self.ymax)
        box = Box.from_shapely(shape)
        self.assertEqual(box.tuple_format(), self.tuple_box)

    def test_get_shapely(self):
        bounds = self.box.get_shapely().bounds
        self.assertEqual((bounds[1], bounds[0], bounds[3], bounds[2]),
                         self.tuple_box)

    def test_make_square(self):
        square = Box.make_square(0, 0, 10)
        tuple_square = ((0, 0, 10, 10))
        self.assertEqual(square.tuple_format(), tuple_square)
        self.assertTrue(square.get_width() == square.get_height())

    def test_make_eroded(self):
        pass

    def test_make_buffer(self):
        pass

    def test_make_copy(self):
        pass

    def test_get_windows(self):
        extent = Box(0, 0, 100, 100)
        windows = list(extent.get_windows(10, 10))
        self.assertEqual(len(windows), 100)

        extent = Box(0, 0, 100, 100)
        windows = list(extent.get_windows(10, 5))
        self.assertEqual(len(windows), 400)

        extent = Box(0, 0, 20, 20)
        windows = set([window.tuple_format()
                       for window in extent.get_windows(10, 10)])
        expected_windows = [
            Box.make_square(0, 0, 10),
            Box.make_square(10, 0, 10),
            Box.make_square(0, 10, 10),
            Box.make_square(10, 10, 10)
        ]
        expected_windows = set([window.tuple_format()
                               for window in expected_windows])
        self.assertSetEqual(windows, expected_windows)
