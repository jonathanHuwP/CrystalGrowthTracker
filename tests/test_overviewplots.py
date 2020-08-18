"""
test_overviewplots.py

This offers tests for the overviewplots module.

Joanna Leng (an EPSRC funded Research Software Engineering Fellow (EP/R025819/1)
University of Leeds
June 2020

Copyright August 2020sk2

---

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import unittest
from unittest import mock
import numpy as np
from cgt import overviewplots as plots


class TestPlotMeans(unittest.TestCase):
    """
    Test the plotmeans function from the overviewplots library
    """
    @mock.patch("%s.plots.plt" % __name__)
    def test_mock_plt_fig(self, mock_plt):
        """
        Tests the means plot.
        """
        print("Start TestPlotMeans test_mock_plt_fig", flush=True)

        numbers = [number for number in range(10)]
        means = np.random.random_sample((10,))

        outpath = 'temp/'
        xlabel = 'Frame'
        ylabel = 'Grayscale value'
        title = 'Mean Across All Video Frames'

        filename_out = plots.plot_means(outpath, numbers, means)
        assert filename_out == "temp//Mean1.png"

        assert mock_plt.title.call_args_list[0][0][0] == title
        assert mock_plt.xlabel.call_args_list[0][0][0] == xlabel
        assert mock_plt.ylabel.call_args_list[0][0][0] == ylabel
#
        assert mock_plt.figure.called


    @mock.patch("%s.plots.plt" % __name__)
    def test_mock_plt_plot(self, mock_plt):
        """
        Tests the calls to plt.plot in the plotmeans function
        from the overviewplots library.
        """
        print("Start TestPlotMeans test_mock_plt_plot", flush=True)

        numbers = [number for number in range(10)]
        means = np.random.random_sample((10,))

        flag = 'b'
        outpath = 'temp/'
        key = "Frame Mean"

        filename_out = plots.plot_means(outpath, numbers, means)
        assert filename_out == "temp//Mean1.png"


        for call in mock_plt.plot.call_args_list:
            args, kwargs = call
            for arg in args:
                self.assertTrue(arg.startswith('PASS') for arg in args)
            for kwarg in kwargs:
                self.assertTrue(kwarg.startswith('PASS') for kwarg in kwargs)

        args, kwargs = mock_plt.plot.call_args_list[0]
        numbers_dash = args[0]
        means_dash = args[1]
        flag_dash = args[2]

        key_hash = kwargs["label"]

        try:
            np.testing.assert_array_equal(numbers, numbers_dash)
            result = True
        except AssertionError as err:
            result = False
            print(err)
        self.assertTrue(result)

        try:
            np.testing.assert_array_almost_equal(means, means_dash)
            result = True
        except AssertionError as err:
            result = False
            print(err)
        self.assertTrue(result)

        assert len(numbers_dash) == len(means)
        assert flag == flag_dash
        assert key == key_hash


if __name__ == '__main__':
    unittest.main()
    