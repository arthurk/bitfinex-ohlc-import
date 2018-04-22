import responses
import pendulum
import unittest

from bitfinex.utils import get_data, date_range


class TestRequest(unittest.TestCase):
    @responses.activate
    def test_success(self):
        """
        Test that a request is made and returns json
        """
        example_response = """
        [
            [
                1518307200000,
                8563,
                8355,
                8570,
                7851,
                40727.5871198
            ]
        ]
        """
        responses.add(responses.GET, 'http://example.org/',
                      body=example_response)
        data = get_data(url='http://example.org')

        assert data == [[1518307200000, 8563, 8355, 8570, 7851, 40727.5871198]]
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == 'http://example.org/'


def test_date_range():
    """
    Test that the iterator yields the correct end-date.
    """
    start_date = pendulum.create(2015, 5, 12)
    end_date = pendulum.create(2015, 5, 13, 15, 0)
    d = pendulum.Interval(minutes=1000)

    ranges = [(d1, d2) for d1, d2 in date_range(start_date, end_date, d)]

    assert len(ranges) == 3

    assert ranges[0][0] == start_date
    assert ranges[0][1] == pendulum.create(2015, 5, 12, 16, 40)

    # the start date of the next element should be the end
    # date of the first one
    assert ranges[1][0] == pendulum.create(2015, 5, 12, 16, 40)
    assert ranges[1][1] == pendulum.create(2015, 5, 13, 9, 20)

    # the last element shouldn't be later than the end date
    assert ranges[2][0] == pendulum.create(2015, 5, 13, 9, 20)
    assert ranges[2][1] == end_date
