# NPI Schedule

Утилита для получения расписания Новочеркасского политехнического института (НПИ) через командную строку.


> `oops/` — экспериментальная реализация в ООП-стиле, созданная исключительно в исследовательских целях (было интересно переписать тот же функционал иначе). **Не поддерживается** и не будет изменяться в последующих обновлениях. Весь новый функционал добавляется только в `main/npi-api.py`.


## Установка

```bash
# Интерактивная (рекомендуется)
make setup

# Или с параметрами
make install FACULT=F GROUP=ИСПа COURSE=3 PORT=8501 DISPLAY=plugin

# Только плагин или conky
make install-plugin
make install-conky

# Удаление
make uninstall
```

`make setup` запросит факультет, группу, курс и установит:
- `~/.local/bin/npi-schedule` — основной скрипт
- `~/.local/bin/_schedule_opts` — быстрая команда с вашими аргументами
- `~/.config/systemd/user/schedule.{service,timer}` — фоновое получение расписания
- Опционально: NoctaliaShell плагин или Conky-конфиг

### Зависимости

- Python 3.11+
- `jq` (для парсинга конфигурации)
- `python-requests`, `python-pandas`

Установка через пакетный менеджер вашего дистрибутива. Пример для Arch:

```bash
sudo pacman -S python-requests python-pandas jq
```

## Использование

```bash
npi-schedule <команда> [аргументы]
```

### Расписание студентов

```bash
npi-schedule student -g ГРУППА -f ФАКУЛЬТЕТ [-c КУРС] [-d ДАТА] [-t]
```

Алиас: `s`

Аргументы:
- `-g, --group` — номер группы (обязательно)
- `-f, --facult` — код факультета (обязательно)
- `-c, --course` — курс (по умолчанию: 1)
- `-d, --date` — дата `YYYY-MM-DD` или список через запятую
- `-t, --tomorrow` — расписание на завтра
- `-0, --finals-schedule` — расписание зачётной недели
- `-m, --max-col-width` — максимальная ширина колонки

### Быстрая команда

```bash
_schedule_opts          # расписание сегодня (с вашими факультетом/группой/курсом)
_schedule_opts -t       # расписание на завтра
_schedule_opts -d 2025-09-01  # на конкретную дату
```

### Преподаватели

```bash
npi-schedule lecturers search Фамилия
npi-schedule lecturers schedule "Фамилия И О" [-d ДАТА]
```

Алиас: `l`

### Аудитории

```bash
npi-schedule auditoriums search НОМЕР
npi-schedule auditoriums schedule АУДИТОРИЯ [-d ДАТА]
```

Алиас: `a`

### Примеры

```bash
npi-schedule s -g ИСПа -f F -c 3
npi-schedule s -g ИСПа -f F -t
npi-schedule l search Иванов
npi-schedule l schedule "Иванов И И" -d 2025-09-01
npi-schedule a search 310
npi-schedule a schedule 310ГЛ -d 2025-09-01,2025-09-02
```

## Коды факультетов

| Код | Аббревиатура | Название |
|-----|--------------|----------|
| 1 | ФГГНГД | Факультет геологии, горного и нефтегазового дела |
| 2 | ФИТУ | Факультет информационных технологий и управления |
| 3 | ИДО | Институт дополнительного образования |
| 4 | АСИиГР | Академия социальных исследований и гуманитарного развития |
| 5 | МФ | Механический факультет |
| 6 | ЭНФ | Энергетический факультет |
| 7 | ТФ | Технологический факультет |
| 8 | СФ | Строительный факультет |
| 9 | АС | Аспирантура |
| A | ИФИО | Институт фундаментального инженерного образования |
| B | ФИОП | Факультет инноватики и организации производства |
| C | ИБ | Информационная безопасность |
| D | ИМО | Институт международного образования |
| F | НПК | Новочеркасский политехнический колледж |

## NoctaliaShell плагин

Включает:
- DesktopWidget с расписанием на сегодня/завтра
- HTTP-демон (`schedule-httpd.service`) для подачи файлов плагину
- Настройка порта через `settings.json`

Порт по умолчанию: 8501 (можно изменить при установке).

После установки плагина перезагрузите Noctalia Shell, чтобы он появился в списке виджетов.

## Conky-виджет

Конфиг `conky/schedule.lua` (вместе с `base.lua`, `colors.lua`) отображает расписание на рабочем столе.
Установка: `make install-conky`

Запуск:
```bash
conky -f ~/.config/conky/schedule.lua
```

## Фоновая служба

`schedule.timer` запускает `schedule.service` через 10с после загрузки,
который получает расписание и сохраняет в `~/.config/schedule/{today,tomorrow}`.

## Структура проекта

```
├── main/npi-api.py           # CLI — основная реализация
├── oops/                     # ООП-версия (экспериментальная, не поддерживается)
├── noctalia-plugin/          # QML плагин для NoctaliaShell
│   ├── DesktopWidget.qml
│   ├── manifest.json
│   ├── settings.json
│   └── http-server.service
├── conky/                    # Conky-виджет
│   ├── base.lua
│   ├── colors.lua
│   └── schedule.lua
├── scripts/
│   ├── schedule-httpd        # HTTP-демон для QML плагина
│   └── _schedule_opts        # Быстрая команда (читает config.json)
├── schedule.sh               # Фоновый скрипт получения расписания
├── schedule.service          # systemd сервис
├── schedule.timer            # systemd таймер
└── Makefile                  # Установка (make setup / make install)
```

