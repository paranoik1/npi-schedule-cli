dofile(os.getenv("HOME") .. "/.config/conky/base.lua")
config = conky.config

config.alignment = 'top_left'
config.maximum_width = 1000
config.gap_y = 10

conky.text = [[
${color0}Расписание в колледже группы '${color}ИСПа${color0}'
$hr
${color0}На сегодня
${color}${exec cat ~/.config/schedule/today}
$hr
${color0}На завтра
${color}${exec cat ~/.config/schedule/tomorrow}
]]
