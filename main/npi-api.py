#!/usr/bin/env python3
from argparse import ArgumentParser, RawTextHelpFormatter
from datetime import datetime, timedelta
from typing import Callable

import pandas as pd
import requests as req

pd.options.display.max_colwidth = 1000
pd.options.display.expand_frame_repr = False


API_URL = "https://schedule.npi-tu.ru/api/"
TIMES = {1: "9:00", 2: "10:45", 3: "13:15", 4: "15:00", 5: "16:45", 6: "18:30"}
FACULTIES = {
    "1": {"code": "ФГГНГД", "name": "Факультет геологии, горного и нефтегазового дела"},
    "2": {"code": "ФИТУ", "name": "Факультет информационных технологий и управления"},
    "3": {"code": "ИДО", "name": "Институт дополнительного образования"},
    "4": {
        "code": "АСИиГР",
        "name": "Академия социальных исследований и гуманитарного развития",
    },
    "5": {"code": "МФ", "name": "Механический факультет"},
    "6": {"code": "ЭНФ", "name": "Энергетический факультет"},
    "7": {"code": "ТФ", "name": "Технологический факультет"},
    "8": {"code": "СФ", "name": "Строительный факультет"},
    "9": {"code": "АС", "name": "Аспирантура"},
    "D": {"code": "ИМО", "name": "Институт международного образования"},
    "A": {"code": "ИФИО", "name": "Институт фундаментального инженерного образования"},
    "C": {"code": "ИБ", "name": "Информационная безопасность"},
    "F": {"code": "НПК", "name": "Новочеркасский политехнический колледж"},
    "B": {"code": "ФИОП", "name": "Факультет инноватики и организации производства"},
}
NOW_DATE = datetime.now().strftime("%Y-%m-%d")
SUBCOMMANDS_ALIASES = [("student", "s"), ("lecturers", "l"), ("auditoriums", "a")]

max_column_width: int | None = None


def add_argument_max_col_width(parser: ArgumentParser):
    parser.add_argument(
        "-m", "--max-col-width",
        help="Максимальная ширина колонки при выводе",
        type=int,
    )


def add_argument_date(parser: ArgumentParser):
    parser.add_argument(
        "-d",
        "--date",
        help="Дата (Year-month-day) или же список дат через запятую, по умолчанию сегодняшняя: "
        + NOW_DATE,
        default=NOW_DATE,
    )


def get_args():
    parser = ArgumentParser("npi-schedule", description="Расписание пар НПИ")
    add_argument_max_col_width(parser)

    subparsers = parser.add_subparsers(dest="subcommand")

    ### NOTE: Подкоманда для получения расписания студентов ###
    epilog = "Список кодов факультетов (-f):\n" + "\n".join(
        [
            key + " - " + value["code"] + " - " + value["name"]
            for key, value in FACULTIES.items()
        ]
    )

    student_parser = subparsers.add_parser(
        SUBCOMMANDS_ALIASES[0][0],
        description="Расписание для студентов",
        aliases=SUBCOMMANDS_ALIASES[0][0:],
        epilog=epilog,
        formatter_class=RawTextHelpFormatter,
    )
    student_parser.add_argument("-g", "--group", help="Группа", required=True)
    student_parser.add_argument(
        "-f", "--facult", help="Факультет", choices=FACULTIES.keys(), required=True
    )
    student_parser.add_argument("-c", "--course", help="Курс", default=1)
    student_parser.add_argument("-0", "--finals-schedule", action="store_true", help="Расписание зачетной недели", default=False, )
    student_parser.add_argument("-t", "--tomorrow", action="store_true", help="Расписание на завтра", default=False)
    add_argument_date(student_parser)
    add_argument_max_col_width(student_parser)


    ### NOTE: Подкоманда для работы с лекторами ###
    lectors_parser = subparsers.add_parser(
        SUBCOMMANDS_ALIASES[1][0], aliases=SUBCOMMANDS_ALIASES[1][0:]
    )
    add_argument_max_col_width(lectors_parser)
    lectors_subparsers = lectors_parser.add_subparsers(
        dest="function", required=True, help="Действия с лекторами"
    )

    lector_searh_parser = lectors_subparsers.add_parser("search", help="Поиск лектора")
    lector_searh_parser.add_argument(
        "query", help="Фамилия или часть фамилии для поиска"
    )
    add_argument_max_col_width(lector_searh_parser)

    lector_schedule_parser = lectors_subparsers.add_parser(
        "schedule", help="Получение расписания лектора"
    )
    lector_schedule_parser.add_argument(
        "lecturer", help='Фамилия и инициалы лектора в формате "Фамилия И О"'
    )
    add_argument_date(lector_schedule_parser)
    add_argument_max_col_width(lector_schedule_parser)


    ### NOTE: Подкоманда для работы с аудиториями ###
    auditoriums_parser = subparsers.add_parser(
        SUBCOMMANDS_ALIASES[2][0], aliases=SUBCOMMANDS_ALIASES[2][0:]
    )
    add_argument_max_col_width(auditoriums_parser)  # <-- ДОБАВЛЕНО

    auditoriums_subparsers = auditoriums_parser.add_subparsers(
        dest="function", required=True, help="Действия с аудиториями"
    )

    auditorium_searh_parser = auditoriums_subparsers.add_parser(
        "search", help="Поиск аудитории"
    )
    auditorium_searh_parser.add_argument(
        "query", help="Номер или часть номер для поиска"
    )
    add_argument_max_col_width(auditorium_searh_parser)  # <-- ДОБАВЛЕНО

    auditorium_schedule_parser = auditoriums_subparsers.add_parser(
        "schedule", help="Получение расписания аудитории"
    )
    auditorium_schedule_parser.add_argument("auditorium", help="Аудитория")
    add_argument_date(auditorium_schedule_parser)
    add_argument_max_col_width(auditorium_schedule_parser)  # <-- ДОБАВЛЕНО

    return parser.parse_args()


def get_json_response(url: str, *args, **kwargs):
    response = req.get(
        url if url.startswith("http") else API_URL + url, *args, **kwargs
    )
    return response.json()


def __print_data_frame(array: list[dict], columns: list[str]):
    data_frame = pd.DataFrame(array, columns=columns)

    if not data_frame.empty:
        print(data_frame.to_string(index=False, max_colwidth=max_column_width))


def __print_schedule(data: dict, date: str, append_function: Callable[[dict, list], None], columns: list[str], data_info: list[dict] | None = None):
    if "," in date:
        date = set(date.split(","))

    def get_set_dates(dates: list[str] | str):
        return set(dates if isinstance(dates, list) else [dates])

    is_date_type_set = isinstance(date, set)
    check_condition = lambda dates: (
        date & get_set_dates(dates) if is_date_type_set else date in dates 
    )

    lesson_list = []
    lessons_dict = {}

    if not data_info:
        data_info = data.get("classes", [])

    for info in data_info:
        _dates = info.get("dates")
        if not _dates:
            _dates = info.get("date")

        if not check_condition(_dates):
            continue

        lesson = info.copy()
        if is_date_type_set:
            intersection_date = date & get_set_dates(_dates)
            new_date = list(intersection_date)[0]

            if not (intersection_date & set(lessons_dict.keys())):
                lessons_dict[new_date] = []

            append_function(lesson, lessons_dict[new_date])
        else:
            append_function(lesson, lesson_list)

    if is_date_type_set:
        for date, lessons in lessons_dict.items():
            print("Расписание на " + date)
            __print_data_frame(lessons, columns)
            print()
    else:
        __print_data_frame(lesson_list, columns)


def print_student_schedule(group: str, facult: str, course: int | str, date: str, is_finals_schedule: bool = False):
    data = get_json_response(
        f"v2/faculties/{facult}/years/{course}/groups/{group}/{'finals-schedule' if is_finals_schedule else 'schedule'}" 
    )

    if is_finals_schedule:
        __print_schedule(
            data=data,
            date=date,
            append_function=lambda lesson, array: array.append(
                [
                    lesson["start"] + "-" + lesson["end"],
                    lesson["auditorium"],
                    lesson["type"] + "-" + lesson["discipline"],
                    lesson["lecturer"],
                ]
            ),
            columns=["Период", "Аудитория", "Дисциплина", "Преподаватель"],
            data_info=data
        )
    else:
        __print_schedule(
            data=data,
            date=date,
            append_function=lambda lesson, array: array.append(
                [
                    TIMES[lesson["class"]],
                    lesson["auditorium"],
                    lesson["type"] + "-" + lesson["discipline"],
                    lesson["lecturer"],
                ]
            ),
            columns=["Начало", "Аудитория", "Дисциплина", "Преподаватель"]
        )


def print_lecturer_schedule(lecturer: str, date: str):
    data = get_json_response(f"v2/lecturers/{lecturer}/schedule")

    print("Лектор: " + data.get("lecturer"))

    __print_schedule(
        data=data,
        date=date,
        append_function=lambda lesson, array: array.append(
            [
                TIMES[lesson["class"]],
                lesson["auditorium"],
                lesson["type"] + "-" + lesson["discipline"],
                lesson["groups"],
            ]
        ),
        columns=["Начало", "Аудитория", "Дисциплина", "Группы"],
    )


def print_auditorium_schedule(auditorium: str, date: str):
    data = get_json_response(f"v2/auditoriums/{auditorium}/schedule")

    __print_schedule(
        data=data,
        date=date,
        append_function=lambda lesson, array: array.append(
            [
                TIMES[lesson["class"]],
                lesson["type"] + "-" + lesson["discipline"],
                lesson["lecturer"],
                lesson["groups"],
            ]
        ),
        columns=["Начало", "Дисциплина", "Педагог", "Группы"],
    )


def print_found_lecturers(query: str):
    data = get_json_response("v1/lecturers/" + query)
    for lecturer in data:
        print(lecturer)


def print_found_auditoriums(query: str):
    data = get_json_response("v1/auditoriums/" + query)

    for corpus, auditoriums in data.items():
        print("Корпус:", corpus)
        for auditorium, type in auditoriums:
            print(auditorium, type)


def main():
    global max_column_width
    
    args = get_args()
    subcommand = args.subcommand
    max_column_width = args.max_col_width

    if hasattr(args, "tomorrow") and args.tomorrow:
        args.date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    if subcommand in SUBCOMMANDS_ALIASES[0]:
        print_student_schedule(args.group, args.facult, args.course, args.date, args.finals_schedule)
    
    elif subcommand in SUBCOMMANDS_ALIASES[1]:
        if args.function == "search":
            print_found_lecturers(args.query)
            return
        
        print_lecturer_schedule(args.lecturer, args.date)

    elif subcommand in SUBCOMMANDS_ALIASES[2]:
        if args.function == "search":
            print_found_auditoriums(args.query)
            return
        
        print_auditorium_schedule(args.auditorium, args.date)


if __name__ == '__main__':
    main()
