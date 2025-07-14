from typing import Any, Callable

from core import Printer
from utils import print_data_frame


class SchedulePrinter(Printer):
    def _print_schedule_list(
        self, data: dict, date: set[str], columns: list[str], append_function: Callable
    ):
        lessons_dict = {}

        for info in data["classes"]:
            dates = info["dates"]
            if not (date & set(dates)):
                continue

            lesson = info.copy()
            intersection_date = date & set(dates)
            new_date = list(intersection_date)[0]

            if not (intersection_date & set(lessons_dict.keys())):
                lessons_dict[new_date] = []

            append_function(lesson, lessons_dict[new_date])

        for date, lessons in lessons_dict.items():
            print("\nРасписание на " + date)
            print_data_frame(lessons, columns)

    def _print_schedule(
        self, data: dict, date: str, columns: list[str], append_function: Callable
    ):
        lesson_list = []
        for info in data["classes"]:
            dates = info["dates"]

            if date in dates:
                lesson = info.copy()
                append_function(lesson, lesson_list)

        print_data_frame(lesson_list, columns)

    def __call__(
        self, data: Any, date: str | set, columns: list[str], append_function
    ) -> Any:
        if isinstance(date, str):
            print_function = self._print_schedule
        else:
            date = set(date)
            print_function = self._print_schedule_list

        print_function(data, date, columns, append_function)


# FIXME: Компактность или читаемость? Что же выбрать?
#
# def __print_schedule(data: dict, date: str, append_function: Callable, columns: list[str]):
#     if "," in date:
#         date = set(date.split(","))

#     is_date_type_set = isinstance(date, set)
#     check_condition = lambda dates: (
#         date & set(dates) if is_date_type_set else date in dates
#     )

#     lesson_list = []
#     lessons_dict = {}

#     for info in data["classes"]:
#         dates = info["dates"]
#         if not check_condition(dates):
#             continue

#         lesson = info.copy()
#         if is_date_type_set:
#             intersection_date = date & set(dates)
#             new_date = list(intersection_date)[0]

#             if not (intersection_date & set(lessons_dict.keys())):
#                 lessons_dict[new_date] = []

#             append_function(lesson, lessons_dict[new_date])
#         else:
#             append_function(lesson, lesson_list)

#     if is_date_type_set:
#         for date, lessons in lessons_dict.items():
#             print("Расписание на " + date)
#             print_data_frame(lessons, columns)
#     else:
#         print_data_frame(lesson_list, columns)


class ListPrinter(Printer):
    def __call__(self, data: Any) -> Any:
        for item in data:
            print(item)


# FIXME: Сделать более универсальный класс Printer: DictPrinter?
class AuditoriumsPrinter(Printer):
    def __call__(self, data: Any) -> Any:
        for corpus, auditoriums in data.items():
            print("\nКорпус:", corpus)
            for auditorium, type in auditoriums:
                print(auditorium, type)
