from argparse import ArgumentParser, Namespace
from typing import Any

from cli_methods import (AuditoriumsScheduleCliMethod,
                         AuditoriumsSearchCliMethod,
                         LecturersScheduleCliMethod, LecturersSearchCliMethod,
                         StudentScheduleCliMethod)
from core import CliMethod, Printer, _SubParsersAction
from printers import AuditoriumsPrinter, ListPrinter, SchedulePrinter
from utils import SUBCOMMANDS_ALIASES, set_global_pandas_max_colwidth


class Main:
    def __init__(self) -> None:
        self.parser = self.create_parser()
        self.create_subparsers()

        list_printer = ListPrinter()
        schedule_printer = SchedulePrinter()
        auditoriums_printer = AuditoriumsPrinter()

        self.cli_methods = {
            SUBCOMMANDS_ALIASES[0]: StudentScheduleCliMethod.factory(
                self.subparsers, schedule_printer
            ),
            SUBCOMMANDS_ALIASES[1]: {
                "search": LecturersSearchCliMethod.factory(
                    self.lecturers_subparsers, list_printer
                ),
                "schedule": LecturersScheduleCliMethod.factory(
                    self.lecturers_subparsers, schedule_printer
                ),
            },
            SUBCOMMANDS_ALIASES[2]: {
                "search": AuditoriumsSearchCliMethod.factory(
                    self.auditoriums_subparsers, auditoriums_printer
                ),
                "schedule": AuditoriumsScheduleCliMethod.factory(
                    self.auditoriums_subparsers, schedule_printer
                ),
            },
        }

    @staticmethod
    def create_parser():
        parser = ArgumentParser("npi-schedule", description="Расписание пар НПИ")
        parser.add_argument(
            "-m",
            "--max-col-width",
            help="Максимальная ширина колонки при выводе",
            default=500,
            type=int,
        )

        return parser

    def create_subparsers(self):
        self.subparsers = self.parser.add_subparsers(dest="subcommand")

        lecturers_parser = self.subparsers.add_parser(
            SUBCOMMANDS_ALIASES[1][0], aliases=SUBCOMMANDS_ALIASES[1][0:]
        )

        self.lecturers_subparsers = lecturers_parser.add_subparsers(
            dest="function", required=True, help="Действия с лекторами"
        )

        auditoriums_parser = self.subparsers.add_parser(
            SUBCOMMANDS_ALIASES[2][0], aliases=SUBCOMMANDS_ALIASES[2][0:]
        )
        self.auditoriums_subparsers = auditoriums_parser.add_subparsers(
            dest="function", required=True, help="Действия с аудиториями"
        )

    def start(self):
        args = self.parser.parse_args()
        subcommand = args.subcommand

        set_global_pandas_max_colwidth(args.max_col_width)

        for aliases, method_or_dict in self.cli_methods.items():
            if subcommand not in aliases:
                continue

            if isinstance(method_or_dict, CliMethod):
                method = method_or_dict
            elif isinstance(method_or_dict, dict):
                method = method_or_dict.get(args.function)
                if method is None:
                    raise ValueError(args.function + " не найден в cli_methods")
            else:
                raise ValueError(
                    "В cli_methods словаре должны находиться Factory or dict"
                )

            method(args)


if __name__ == "__main__":
    main = Main()
    main.start()
