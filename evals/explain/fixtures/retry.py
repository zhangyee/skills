def fetch_with_retry(fetch):
    for attempt in range(3):
        try:
            return fetch()
        except TimeoutError:
            if attempt == 2:
                raise
