from argparse import ArgumentParser, Namespace, _SubParsersAction
from typing import Any

import requests


class ApiEndpoint:
    API_URL = "https://schedule.npi-tu.ru/api/"

    def __init__(self, endpoint) -> None:
        self.url = self.API_URL + endpoint

    def __call__(self, *url_args, **url_kwargs: Any) -> Any:
        response = requests.get(self.url.format(*url_args, **url_kwargs))
        if response.status_code != 200:
            raise requests.HTTPError(response.status_code)

        return response.json()


class Printer:
    def __call__(self, data: Any, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()


class CliMethod:
    def __init__(
        self, subparsers: _SubParsersAction, api_endpoint: ApiEndpoint, printer: Printer
    ) -> None:
        self.subparsers = subparsers
        self.api_endpoint = api_endpoint
        self.printer = printer

        self._add_args()

    def __call__(self, args: Namespace) -> Any:
        raise NotImplementedError()

    def _add_args(self):
        raise NotImplementedError()

    def get_data(self, *url_args, **url_kwargs):
        return self.api_endpoint(*url_args, **url_kwargs)

    def print(self, data: Any, *args, **kwargs):
        self.printer(data, *args, **kwargs)

    @classmethod
    def factory(cls, subparsers: _SubParsersAction, printer: Printer) -> "CliMethod":
        raise NotImplementedError()
