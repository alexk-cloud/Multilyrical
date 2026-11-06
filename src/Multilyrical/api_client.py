import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retries = Retry(
    total=2,
    connect=2,
    read=2,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET"],
    respect_retry_after_header=True
)

session.mount("https://", HTTPAdapter(max_retries=retries))