from argparse import ArgumentParser
from datetime import datetime

import pandas

pandas.options.display.expand_frame_repr = False


SUBCOMMANDS_ALIASES = [("schedule", "s"), ("lecturers", "l"), ("auditoriums", "a")]
NOW_DATE = datetime.now().strftime("%Y-%m-%d")
TIMES = {1: "9:00", 2: "10:45", 3: "13:15", 4: "15:00", 5: "16:45", 6: "18:30"}


def get_time(lesson_class: int) -> str | None:
    return TIMES.get(lesson_class)


def add_argument_date(parser: ArgumentParser) -> None:
    parser.add_argument(
        "-d",
        "--date",
        help="Дата (Year-month-day) или же список дат через запятую, по умолчанию сегодняшняя: "
        + NOW_DATE,
        default=NOW_DATE,
    )


def print_data_frame(data: list, columns: list):
    data_frame = pandas.DataFrame(data, columns=columns)

    if not data_frame.empty:
        data_frame_string = data_frame.to_string(
            index=False, max_colwidth=pandas.options.display.max_colwidth
        )

        print(data_frame_string)


def set_global_pandas_max_colwidth(colwidth: int):
    pandas.options.display.max_colwidth = colwidth
