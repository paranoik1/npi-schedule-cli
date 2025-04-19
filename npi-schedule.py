#!/usr/bin/env python
import requests as req
import pandas as pd

from datetime import datetime
from argparse import ArgumentParser, RawTextHelpFormatter


pd.options.display.max_colwidth = 1000
pd.options.display.expand_frame_repr = False


API_URL = "https://schedule.npi-tu.ru/api/"
TIMES = {
	1: "9:00",
	2: "10:45",
	3: "13:15",
	4: "15:00",
	5: "16:45",
	6: "18:30"
}
FACULTIES = {
  "1": {
	"code": "ФГГНГД",
	"name": "Факультет геологии, горного и нефтегазового дела"
  },
  "2": {
	"code": "ФИТУ",
	"name": "Факультет информационных технологий и управления"
  },
  "3": {
	"code": "ИДО",
	"name": "Институт дополнительного образования"
  },
  "4": {
	"code": "АСИиГР",
	"name": "Академия социальных исследований и гуманитарного развития"
  },
  "5": {
	"code": "МФ",
	"name": "Механический факультет"
  },
  "6": {
	"code": "ЭНФ",
	"name": "Энергетический факультет"
  },
  "7": {
	"code": "ТФ",
	"name": "Технологический факультет"
  },
  "8": {
	"code": "СФ",
	"name": "Строительный факультет"
  },
  "9": {
	"code": "АС",
	"name": "Аспирантура"
  },
  "D": {
	"code": "ИМО",
	"name": "Институт международного образования"
  },
  "A": {
	"code": "ИФИО",
	"name": "Институт фундаментального инженерного образования"
  },
  "C": {
	"code": "ИБ",
	"name": "Информационная безопасность"
  },
  "F": {
	"code": "НПК",
	"name": "Новочеркасский политехнический колледж"
  },
  "B": {
	"code": "ФИОП",
	"name": "Факультет инноватики и организации производства"
  }
}
NOW_DATE = datetime.now().strftime("%Y-%m-%d")
SUBCOMMANDS_ALIASES = [
	("student", "s"),
	("lecturers", "l"),
	("auditoriums", "a")
]


def add_argument_date(parser: ArgumentParser):
	parser.add_argument("-d", "--date", help="Дата (Year-month-day) или же список дат через запятую, по умолчанию сегодняшняя: " + NOW_DATE, default=NOW_DATE)


def get_args():
	parser = ArgumentParser("npi-schedule", description="Расписание пар НПИ")

	subparsers = parser.add_subparsers(dest="subcommand")

	# Подкоманда для получения расписания студентов
	epilog = "Список кодов факультетов (-f):\n" + "\n".join([key + " - " + value["code"] + " - " + value["name"] for key, value in FACULTIES.items()])

	student_parser = subparsers.add_parser(SUBCOMMANDS_ALIASES[0][0], description="Расписание для студентов", aliases=SUBCOMMANDS_ALIASES[0][0:], epilog=epilog, formatter_class=RawTextHelpFormatter)
	student_parser.add_argument("-g", "--group", help="Группа", required=True)
	student_parser.add_argument("-f", "--facult", help="Факультет", choices=FACULTIES.keys(), required=True)
	student_parser.add_argument("-c", "--course", help="Курс", default=1)
	add_argument_date(student_parser)


	# Подкоманда для работы с лекторами
	lectors_parser = subparsers.add_parser(SUBCOMMANDS_ALIASES[1][0], aliases=SUBCOMMANDS_ALIASES[1][0:])
	lectors_subparsers = lectors_parser.add_subparsers(dest="function", required=True, help='Действия с лекторами')

	lector_searh_parser = lectors_subparsers.add_parser("search", help="Поиск лектора")
	lector_searh_parser.add_argument("query", help="Фамилия или часть фамилии для поиска")

	lector_schedule_parser = lectors_subparsers.add_parser("schedule", help="Получение расписания лектора")
	lector_schedule_parser.add_argument("lecturer", help="Фамилия и инициалы лектора в формате \"Фамилия И О\"")
	add_argument_date(lector_schedule_parser)


	# Подкоманда для работы с аудиториями
	auditoriums_parser = subparsers.add_parser(SUBCOMMANDS_ALIASES[2][0], aliases=SUBCOMMANDS_ALIASES[2][0:])
	auditoriums_subparsers = auditoriums_parser.add_subparsers(dest="function", required=True, help='Действия с аудиториями')

	auditorium_searh_parser = auditoriums_subparsers.add_parser("search", help="Поиск аудитории")
	auditorium_searh_parser.add_argument("query", help="Номер или часть номер для поиска")

	auditorium_schedule_parser = auditoriums_subparsers.add_parser("schedule", help="Получение расписания аудитории")
	auditorium_schedule_parser.add_argument("auditorium", help="Аудитория")
	add_argument_date(auditorium_schedule_parser)


	return parser.parse_args()


def __get_json_response(url: str, *args, **kwargs):
	response = req.get(url if url.startswith("http") else API_URL + url, *args, **kwargs)
	return response.json()


def __print_data_frame(array: list, columns: list):
	data_frame = pd.DataFrame(
		array,
		columns=columns
	)

	if not data_frame.empty:
		print(data_frame.to_string(index=False))


def __print_schedule(data: dict, date: str, append_function, columns):
	if "," in date:
		date = set(date.split(","))

	is_date_type_set = isinstance(date, set)
	check_condition = lambda dates: date & set(dates) if is_date_type_set else date in dates

	lesson_list = []
	lessons_dict = {}

	for info in data["classes"]:
		dates = info["dates"]
		if not check_condition(dates):
			continue

		lesson = info.copy()
		if is_date_type_set:
			intersection_date = date & set(dates)
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



def print_student_schedule(group: str, facult: str, course: int | str, date: str):
	data = __get_json_response(f'v2/faculties/{facult}/years/{course}/groups/{group}/schedule')

	__print_schedule(
		data=data,
		date=date,
		append_function=lambda lesson, array: array.append([
			TIMES[lesson["class"]],
			lesson["auditorium"],
			lesson["type"] + "-" + lesson["discipline"],
			lesson["lecturer"]
		]),
		columns=["Начало", "Аудитория", "Дисциплина", "Прдподаватель"]
	)


def print_lecturer_schedule(lecturer: str, date: str):
	data = __get_json_response(f"v2/lecturers/{lecturer}/schedule")

	print("Лектор: " + data.get("lecturer"))

	__print_schedule(
		data=data,
		date=date,
		append_function=lambda lesson, array: array.append([
			TIMES[lesson["class"]],
			lesson["auditorium"],
			lesson["type"] + "-" + lesson["discipline"],
			lesson["groups"]
		]),
		columns=["Начало", "Аудитория", "Дисциплина", "Группы"]
	)


def print_auditorium_schedule(auditorium: str, date: str):
	data = __get_json_response(f"v2/auditoriums/{auditorium}/schedule")

	__print_schedule(
		data=data,
		date=date,
		append_function=lambda lesson, array: array.append([
			TIMES[lesson["class"]],
			lesson["type"] + "-" + lesson["discipline"],
			lesson["lecturer"],
			lesson["groups"],
		]),
		columns=["Начало", "Дисциплина", "Педагог", "Группы"]
	)


def print_found_lecturers(query: str):
	data = __get_json_response('v1/lecturers/' + query)
	for lecturer in data:
		print(lecturer)


def print_found_auditoriums(query: str):
	data = __get_json_response('v1/auditoriums/' + query)

	for corpus, auditoriums in data.items():
		print("Корпус:", corpus)
		for auditorium, type in auditoriums:
			print(auditorium, type)


args = get_args()
subcommand = args.subcommand

if subcommand in SUBCOMMANDS_ALIASES[0]:
	print_student_schedule(args.group, args.facult, args.course, args.date)
elif subcommand in SUBCOMMANDS_ALIASES[1]:
	if args.function == "search":
		print_found_lecturers(args.query)
	else:
		print_lecturer_schedule(args.lecturer, args.date)
else:
	if args.function == "search":
		print_found_auditoriums(args.query)
	else:
		print_auditorium_schedule(args.auditorium, args.date)