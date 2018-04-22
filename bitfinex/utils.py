import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


def requests_retry_session(url, retries=3, backoff_factor=1,
                           status_forcelist=(429, 500, 502, 503, 504),
                           session=None):
    """
    Configuration for `requests` retries.

    Args:
        url: url to get
        retries: total number of retry attempts
        backoff_factor: amount of time between attempts
        status_forcelist: retry if response is in list
        session: requests session object

    Example:
        req = requests_retry_session().get(<url>)
    """
    session = session or requests.Session()
    retry = Retry(total=retries,
                  backoff_factor=backoff_factor,
                  status_forcelist=status_forcelist)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session.get(url)


def get_data(url):
    """
    Returns the json data for url
    """
    return requests_retry_session(url).json()


def date_range(start, end, step):
    """
    Generator that yields a tuple of datetime-like objects
    which are `step` apart until the final `end` date
    is reached.
    """
    curr = start
    while curr < end:
        next_ = curr+step
        # next step is bigger than end date
        # yield last (shorter) step until final date
        if next_ > end:
            yield curr, end
            break
        else:
            yield curr, next_
            curr += step
