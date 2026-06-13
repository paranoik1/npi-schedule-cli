import json
import sys
from os import getenv


HOME = getenv('HOME')
PLUGINS_SETTINGS_PATH = f"{HOME}/.config/noctalia/plugins.json"


if len(sys.argv) < 2:
    raise ValueError("Не была получена команда")


command = sys.argv[1]


with open(PLUGINS_SETTINGS_PATH) as fp:
    plugins_settings = json.load(fp)


if 'states' not in plugins_settings:
    raise ValueError(f'В {PLUGINS_SETTINGS_PATH} нет ключа "states". Неизвестный формат конфигурации плагинов')


states = plugins_settings['states']


def save_settings():
    with open(PLUGINS_SETTINGS_PATH, "w") as fp: 
        json.dump(plugins_settings, fp, indent=4)


match (command):
    case 'install':
        states['npi-schedule-plugin'] = {
            'enabled': True,
            'sourceUrl': "https://github.com/paranoik1/npi-schedule-cli"
        }

        save_settings()

        print('Noctalia плагин добавлен в среду')

    case 'uninstall':
        if 'npi-schedule-plugin' not in states:
            print('Плагина нет в настройках')
            exit()

        del plugins_settings['states']['npi-schedule-plugin']
        save_settings()

        print('Noctalia плашиг успешно удален со среды')
    case _:
        raise ValueError('Неизвестная команда: ' + command)
