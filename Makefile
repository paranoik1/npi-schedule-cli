BINDIR ?= $(HOME)/.local/bin
CONFIGDIR ?= $(HOME)/.config/schedule
SYSTEMDDIR ?= $(HOME)/.config/systemd/user
PLUGINDIR ?= $(HOME)/.local/share/noctaliashell/plugins/npi-schedule
CONKYDIR ?= $(HOME)/.config/conky

FACULT ?=
GROUP ?=
COURSE ?=
PORT ?=
DISPLAY ?=

PYTHON ?= python3
SHELL := /bin/bash

.PHONY: all setup install install-bin install-config install-service install-plugin install-conky uninstall

all:
	@echo "Цели:"
	@echo "  make setup           — интерактивная установка (запросит все параметры)"
	@echo "  make install         — установка (FACULT=... GROUP=... COURSE=... PORT=... DISPLAY=plugin|conky|none)"
	@echo "  make install-plugin  — установить QML плагин для NoctaliaShell"
	@echo "  make install-conky   — установить conky-конфиг"
	@echo "  make uninstall       — удалить всё"
	@echo ""
	@echo "Параметры install:"
	@echo "  FACULT=  код факультета (1-9, A, B, C, D, F)"
	@echo "  GROUP=   группа (напр. ИСПа)"
	@echo "  COURSE=  курс (1-4)"
	@echo "  PORT=    порт HTTP-сервера"
	@echo "  DISPLAY= plugin | conky | none"

setup:
	@read -p "Факультет (1-9, A, B, C, D, F): " f; \
	 read -p "Группа: " g; \
	 read -p "Курс (1-4): " c; \
	 read -p "Порт HTTP-сервера: " p; \
	 echo ""; \
	 echo "Выберите отображение:"; \
	 echo "  1) NoctaliaShell QML-плагин"; \
	 echo "  2) Conky-виджет"; \
	 echo "  3) Пропустить"; \
	 read -p "Ваш выбор [1/2/3]: " d; \
	 case "$$d" in \
	   1) disp=plugin ;; \
	   2) disp=conky ;; \
	   *) disp=none ;; \
	 esac; \
	 $(MAKE) install \
	   FACULT="$$f" \
	   GROUP="$$g" \
	   COURSE="$$c" \
	   PORT="$$p" \
	   DISPLAY="$$disp"

install: install-bin install-config install-service install-display

install-bin:
	install -d "$(BINDIR)"
	install main/npi-api.py "$(BINDIR)/npi-schedule"
	install scripts/schedule-httpd "$(BINDIR)/schedule-httpd"
	install schedule.sh "$(BINDIR)/schedule.sh"

install-config:
	@if [ -z "$(FACULT)" ] || [ -z "$(GROUP)" ] || [ -z "$(COURSE)" ] || [ -z "$(PORT)" ]; then \
	  echo "Ошибка: FACULT, GROUP, COURSE и PORT должны быть заданы." >&2; \
	  echo "Используйте 'make setup' или 'make install FACULT=... GROUP=... COURSE=... PORT=...'" >&2; \
	  exit 1; \
	fi
	install -d "$(CONFIGDIR)"
	install scripts/_schedule_opts "$(BINDIR)/_schedule_opts"
	@echo '{' > "$(CONFIGDIR)/config.json"
	@echo '    "faculty": "$(FACULT)",' >> "$(CONFIGDIR)/config.json"
	@echo '    "group": "$(GROUP)",' >> "$(CONFIGDIR)/config.json"
	@echo '    "course": $(COURSE),' >> "$(CONFIGDIR)/config.json"
	@echo '    "port": $(PORT)' >> "$(CONFIGDIR)/config.json"
	@echo '}' >> "$(CONFIGDIR)/config.json"

install-service:
	install -d "$(SYSTEMDDIR)"
# 	sed "s|%h|$(HOME)|g" schedule.service > "$(SYSTEMDDIR)/schedule.service"
# 	sed "s|%h|$(HOME)|g" schedule.timer > "$(SYSTEMDDIR)/schedule.timer"
# 	sed "s|%h|$(HOME)|g" noctalia-plugin/http-server.service > "$(SYSTEMDDIR)/schedule-httpd.service"
	-systemctl --user daemon-reload

install-display:
ifeq ($(DISPLAY),plugin)
	$(MAKE) install-plugin
	-systemctl --user enable --now schedule-httpd.service 2>/dev/null || true
	@echo "HTTP-сервер запущен на порту $(PORT)"
else ifeq ($(DISPLAY),conky)
	$(MAKE) install-conky
else
	@echo "Отображение не настроено. Запустите 'make install-plugin' или 'make install-conky' позже."
endif
	-systemctl --user enable --now schedule.timer 2>/dev/null || true
	-systemctl --user enable --now schedule.service 2>/dev/null || true

install-plugin:
	install -d "$(PLUGINDIR)"
	cp -r noctalia-plugin/* "$(PLUGINDIR)/"
	@echo '{' > "$(PLUGINDIR)/settings.json"
	@echo '    "serverPort": "$(PORT)"' >> "$(PLUGINDIR)/settings.json"
	@echo '}' >> "$(PLUGINDIR)/settings.json"

install-conky:
	install -d "$(CONKYDIR)"
	cp conky/{base,colors,schedule}.lua "$(CONKYDIR)/"

uninstall:
	-systemctl --user disable --now schedule.timer 2>/dev/null || true
	-systemctl --user disable --now schedule.service 2>/dev/null || true
	-systemctl --user disable --now schedule-httpd.service 2>/dev/null || true
	rm -f "$(BINDIR)/npi-schedule"
	rm -f "$(BINDIR)/schedule-httpd"
	rm -f "$(BINDIR)/schedule.sh"
	rm -f "$(BINDIR)/_schedule_opts"
	rm -f "$(SYSTEMDDIR)/schedule.service"
	rm -f "$(SYSTEMDDIR)/schedule.timer"
	rm -f "$(SYSTEMDDIR)/schedule-httpd.service"
	rm -rf "$(PLUGINDIR)"
	rm -f "$(CONKYDIR)"/{base,colors,schedule}.lua
	-systemctl --user daemon-reload
	@echo "Конфиг $(CONFIGDIR) НЕ удалён (там могут быть сохранённые расписания)."
	@echo "Чтобы удалить его вручную: rm -rf $(CONFIGDIR)"
	@echo "Готово."
