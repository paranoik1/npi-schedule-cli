#!/bin/bash
# Фоновое получение расписания.
# Запускается systemd-сервисом schedule.service.

SCHEDULE_CMD="$HOME/.local/bin/_schedule_opts"
SCHEDULE_DIR="$HOME/.config/schedule"
MAX_COL_WIDTH=200

if [ ! -f "$SCHEDULE_CMD" ]; then
    SCHEDULE_CMD="$HOME/.local/bin/npi-schedule"
fi

mkdir -p "$SCHEDULE_DIR"

# Ожидание интернета
echo "Ожидание интернет-соединения..."
while ! ping -q -c 1 google.com > /dev/null 2>&1; do
    sleep 5
done
echo "Соединение установлено."

# Получение расписания (с повторными попытками)
echo "Получение расписания..."
while true; do
    TODAY=$(date +%Y-%m-%d)
    TOMORROW=$(date -d "+1 day" +%Y-%m-%d 2>/dev/null || date -v+1d +%Y-%m-%d)

    if $SCHEDULE_CMD -m "$MAX_COL_WIDTH" > "$SCHEDULE_DIR/today" 2>/dev/null; then
        $SCHEDULE_CMD -m "$MAX_COL_WIDTH" -d "$TOMORROW" > "$SCHEDULE_DIR/tomorrow" 2>/dev/null
        echo "Расписание сохранено."
        break
    else
        echo "Не удалось получить расписание. Повтор через 10с..."
        sleep 10
    fi
done
