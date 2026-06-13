import QtQuick
import QtQuick.Layouts
import qs.Commons
import qs.Modules.DesktopWidgets
import qs.Widgets


DraggableDesktopWidget {
    id: root

    property var pluginApi: null

    property string serverUrl
    property string todayPath
    property string tomorrowPath

    property string todayContent: "Загрузка..."
    property string tomorrowContent: "Загрузка..."

    property int baseWidth: 120
    property int baseHeight: 160

    implicitWidth: Math.round(baseWidth * widgetScale)
    implicitHeight: Math.round(baseHeight * widgetScale)

    function loadSchedule(filePath, targetProperty) {
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200 || xhr.status === 0) {
                    var text = xhr.responseText.trim();
                    root[targetProperty] = text === "" ? "Нет событий" : text;
                } else {
                    root[targetProperty] = "Ошибка загрузки\n" + filePath;
                }
            }
        };
        xhr.open("GET", filePath, true);
        xhr.send();
    }

    function initSettings() {
        if (!pluginApi || !pluginApi.settings)
            return;

        var port = pluginApi.settings.serverPort || 8501;
        serverUrl = "http://127.0.0.1:" + port + "/";
        todayPath = serverUrl + "today";
        tomorrowPath = serverUrl + "tomorrow";
    }

    Component.onCompleted: {
        initSettings();
        loadSchedule(root.todayPath, "todayContent");
        loadSchedule(root.tomorrowPath, "tomorrowContent");
    }

    Timer {
        interval: 300000
        running: true
        repeat: true
        onTriggered: {
            loadSchedule(root.todayPath, "todayContent");
            loadSchedule(root.tomorrowPath, "tomorrowContent");
        }
    }

    ColumnLayout {
        id: contentLayout
        anchors.fill: parent
        anchors.margins: Math.round(Style.marginL * widgetScale)
        spacing: Math.round(Style.marginM * widgetScale)

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

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Math.round(1 * widgetScale)
            Layout.topMargin: Math.round(Style.marginS * widgetScale)
            Layout.bottomMargin: Math.round(Style.marginS * widgetScale)
            color: Color.mOutlineVariant
            opacity: 0.5
        }

        NText {
            text: "Завтра"
            pointSize: Math.round(Style.fontSizeL * widgetScale)
            font.weight: Font.Bold
            color: Color.mPrimary
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

        Item {
            Layout.fillHeight: true
        }
    }
}
