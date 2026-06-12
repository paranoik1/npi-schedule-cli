#!/bin/bash
schedule=~/.local/bin/schedule
# Функция для проверки соединения с интернетом
check_internet() {
  ping -q -c 2 google.com > /dev/null 2>&1
  return $?
}

DIR_INFO=$HOME/.config/schedule/
if [ ! -d "$DIR_INFO" ]; then
  mkdir -p "$DIR_INFO"
  echo "Директория '$DIR_INFO' была создана."
fi

echo $PATH
# Ждем соединения с интернетом
echo "Waiting for internet connection..."
while ! check_internet; do
  sleep 5
done
echo "Internet connection established."

# Проверка файла schedule/today
# today=$(date +%Y-%m-%d)
schedule_file="$DIR_INFO/today"

# if [ -f "$schedule_file" ]; then
#   file_date=$(stat -c %y "$schedule_file" | cut -d ' ' -f 1)
#   if [ "$file_date" == "$today" ]; then
#     echo "Расписание уже было получено"
#     exit 0
#   fi
# fi

# Цикл: пытаемся получить расписание, пока не получится
echo "Получение нового расписания..."
while true; do
  if $schedule -m 40 > "$schedule_file" && \
     $schedule -m 40 -d "$(date -d "+1 day" +"%Y-%m-%d")" > "$DIR_INFO/tomorrow"; then
    echo "Расписание успешно получено."
    break
  else
    echo "Не удалось получить расписание. Повторная попытка через 10 секунд..."
    sleep 10
  fi
done
