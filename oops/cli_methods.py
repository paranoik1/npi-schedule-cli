from argparse import Namespace, RawTextHelpFormatter
from typing import Any

from core import ApiEndpoint, CliMethod
from utils import SUBCOMMANDS_ALIASES, add_argument_date, get_time

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


class ScheduleMixin:
    @staticmethod
    def date_format(date: str) -> str | set[str]:
        if "," in date:
            return set(date.split(","))

        return date

    def _get_lesson(self, time: str, lesson: dict[str]):
        raise NotImplementedError()

    def __append_function(self, lesson: dict[str], lesson_list: list[dict[str]]):
        time = get_time(lesson["class"])

        lesson_item = self._get_lesson(time, lesson)
        lesson_list.append(lesson_item)

    def print(self, data: dict[str], date: str):
        date = self.date_format(date)
        super().print(data, date, self.COLUMNS, self.__append_function)


class StudentScheduleCliMethod(ScheduleMixin, CliMethod):
    ALIASES = SUBCOMMANDS_ALIASES[0]
    COLUMNS = ["Начало", "Аудитория", "Дисциплина", "Прдподаватель"]

    def __call__(self, args: Namespace) -> Any:
        data = self.get_data(group=args.group, facult=args.facult, course=args.course)
        self.print(data, args.date)

    def _add_args(self):
        epilog = "Список кодов факультетов (-f):\n" + "\n".join(
            [
                key + " - " + value["code"] + " - " + value["name"]
                for key, value in FACULTIES.items()
            ]
        )

        student_parser = self.subparsers.add_parser(
            self.ALIASES[0],
            description="Расписание для студентов",
            aliases=self.ALIASES[0:],
            epilog=epilog,
            formatter_class=RawTextHelpFormatter,
        )
        student_parser.add_argument("-g", "--group", help="Группа", required=True)
        student_parser.add_argument(
            "-f", "--facult", help="Факультет", choices=FACULTIES.keys(), required=True
        )
        student_parser.add_argument("-c", "--course", help="Курс", default=1)
        add_argument_date(student_parser)

    def _get_lesson(self, time: str, lesson: dict[str]):
        return [
            time,
            lesson["auditorium"],
            lesson["type"] + "-" + lesson["discipline"],
            lesson["lecturer"],
        ]

    @classmethod
    def factory(cls, subparsers, schedule_printer):
        student_api_endpoint = ApiEndpoint(
            "v2/faculties/{facult}/years/{course}/groups/{group}/schedule"
        )

        return cls(subparsers, student_api_endpoint, schedule_printer)


class LecturersSearchCliMethod(CliMethod):
    def __call__(self, args: Namespace) -> Any:
        data = self.get_data(args.query)
        self.print(data)

    def _add_args(self):
        lector_searh_parser = self.subparsers.add_parser("search", help="Поиск лектора")
        lector_searh_parser.add_argument(
            "query", help="Фамилия или часть фамилии для поиска"
        )

    @classmethod
    def factory(cls, subparsers, list_printer):
        api_endpoint = ApiEndpoint("v1/lecturers/{}")

        return cls(subparsers, api_endpoint, list_printer)


class LecturersScheduleCliMethod(ScheduleMixin, CliMethod):
    COLUMNS = ["Начало", "Аудитория", "Дисциплина", "Группы"]

    def __call__(self, args: Namespace) -> Any:
        data = self.get_data(args.lecturer)
        self.print(data, args.date)

    def _add_args(self):
        lector_schedule_parser = self.subparsers.add_parser(
            "schedule", help="Получение расписания лектора"
        )
        lector_schedule_parser.add_argument(
            "lecturer",
            help='Фамилия и инициалы лектора в формате "Фамилия И О" (без точек)',
        )
        add_argument_date(lector_schedule_parser)

    def _get_lesson(self, time: str, lesson: dict[str]):
        return [
            time,
            lesson["auditorium"],
            lesson["type"] + "-" + lesson["discipline"],
            lesson["groups"],
        ]

    @classmethod
    def factory(cls, subparsers, schedule_printer):
        api_endpoint = ApiEndpoint("v2/lecturers/{}/schedule")

        return cls(subparsers, api_endpoint, schedule_printer)


class AuditoriumsSearchCliMethod(CliMethod):
    def __call__(self, args: Namespace) -> Any:
        data = self.get_data(args.query)
        self.print(data)

    def _add_args(self):
        auditorium_searh_parser = self.subparsers.add_parser(
            "search", help="Поиск аудитории"
        )
        auditorium_searh_parser.add_argument(
            "query", help="Номер или часть номер для поиска"
        )

    @classmethod
    def factory(cls, subparsers, auditoriums_printer):
        api_endpoint = ApiEndpoint("v1/auditoriums/{}")

        return cls(subparsers, api_endpoint, auditoriums_printer)


class AuditoriumsScheduleCliMethod(ScheduleMixin, CliMethod):
    COLUMNS = ["Начало", "Дисциплина", "Педагог", "Группы"]

    def __call__(self, args: Namespace) -> Any:
        data = self.get_data(args.auditorium)
        self.print(data, args.date)

    def _add_args(self):
        auditorium_schedule_parser = self.subparsers.add_parser(
            "schedule", help="Получение расписания аудитории"
        )
        auditorium_schedule_parser.add_argument("auditorium", help="Аудитория")
        add_argument_date(auditorium_schedule_parser)

    def _get_lesson(self, time: str, lesson: dict[str]):
        return [
            time,
            lesson["type"] + "-" + lesson["discipline"],
            lesson["lecturer"],
            lesson["groups"],
        ]

    @classmethod
    def factory(cls, subparsers, schedule_printer):
        api_endpoint = ApiEndpoint("v2/auditoriums/{}/schedule")

        return cls(subparsers, api_endpoint, schedule_printer)
