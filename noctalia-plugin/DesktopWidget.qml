import QtQuick
import QtQuick.Layouts
import qs.Commons
import qs.Modules.DesktopWidgets
import qs.Widgets


DraggableDesktopWidget {
    id: root

    // Обязательное свойство для API плагина
    property var pluginApi: null

    // Пути к файлам. ЗАМЕНИТЕ 'ВАШ_ЮЗЕРНЕЙМ' на ваше реальное имя пользователя!
    // Пример: "file:///home/alex/.config/schedule/today"
    property string serverUrl: "http://0.0.0.0:8000/"
    property string todayPath: serverUrl + "today"
        
    property string tomorrowPath: serverUrl + "tomorrow"

    // Состояние для хранения прочитанного текста
    property string todayContent: "Загрузка..."
    property string tomorrowContent: "Загрузка..."

    // Динамический расчет размеров на основе контента + отступы, с учетом масштабирования
    implicitWidth: Math.round(contentLayout.implicitWidth * widgetScale)
    implicitHeight: Math.round(contentLayout.implicitHeight * widgetScale)
    
    width: implicitWidth
    height: implicitHeight

    // Функция для асинхронного чтения файла
    function loadSchedule(filePath, targetProperty) {
        var xhr = new XMLHttpRequest();
        Logger.i('!!!!!!!!!!!!!!!NPI SHEDULE!!!!!!!!!!!!!!')
        Logger.i(widgetData.tomorrowPath);
        xhr.onreadystatechange = function() {
            Logger.i('Status code: ' + xhr.status + ". State: " + xhr.readyState)

            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200 || xhr.status === 0) {
                    var text = xhr.responseText.trim();
                    root[targetProperty] = text === "" ? "Нет событий" : text;
                    Logger.i(root[targetProperty])
                } else {
                    root[targetProperty] = "Файл не найден.\nПроверьте путь:\n" + filePath.replace("file://", "");
                }
            } 
        };
        xhr.open("GET", filePath, true);
        xhr.send();

    }

    // Загрузка при старте
    Component.onCompleted: {
        loadSchedule(root.todayPath, "todayContent");
        loadSchedule(root.tomorrowPath, "tomorrowContent");
    }

    // Автообновление каждые 5 минут (300000 мс)
    Timer {
        interval: 300000
        running: true
        repeat: true
        onTriggered: {
            loadSchedule(root.todayPath, "todayContent");
            loadSchedule(root.tomorrowPath, "tomorrowContent");
        }
    }

    // Основной контейнер контента
    ColumnLayout {
        id: contentLayout
        anchors.fill: parent
        anchors.margins: Math.round(Style.marginL * widgetScale)
        spacing: Math.round(Style.marginM * widgetScale)

        // --- СЕКЦИЯ: СЕГОДНЯ ---
        NText {
            text: "Сегодня"
            pointSize: Math.round(Style.fontSizeL * widgetScale)
            font.weight: Font.Bold
            color: Color.mPrimary
            Layout.alignment: Qt.AlignLeft
        }

        NText {
            text: root.todayContent
            pointSize: Math.round(Style.fontSizeM * widgetScale)
            color: Color.mOnSurface
            font.family: "monospace" 
            opacity: root.isScaling ? 0.7 : 1.0
            Behavior on opacity {
                enabled: !root.isScaling && !root.isDragging
                NumberAnimation { duration: 150 }
            }
        }

        // Разделитель
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Math.round(1 * widgetScale)
            Layout.topMargin: Math.round(Style.marginS * widgetScale)
            Layout.bottomMargin: Math.round(Style.marginS * widgetScale)
            color: Color.mOutlineVariant
            opacity: 0.5
        }

        // --- СЕКЦИЯ: ЗАВТРА ---
        NText {
            text: "Завтра"
            pointSize: Math.round(Style.fontSizeL * widgetScale)
            font.weight: Font.Bold
            color: Color.mPrimary
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignLeft
        }

        NText {
            text: root.tomorrowContent
            pointSize: Math.round(Style.fontSizeM * widgetScale)
            color: Color.mOnSurface
            font.family: "monospace" 
            opacity: root.isScaling ? 0.7 : 1.0
            Behavior on opacity {
                enabled: !root.isScaling && !root.isDragging
                NumberAnimation { duration: 150 }
            }
        }
    }
}
