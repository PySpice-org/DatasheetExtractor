/***************************************************************************************************
 *
 * DatasheetExtractor - A Python library to extract data from datasheet
 * Copyright (C) 2022 Fabrice Salvaire
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 ***************************************************************************************************/

import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Layouts 1.11

ToolBar {
    id: root

    /*******************************************************
     *
     * API
     *
     */

    property alias message: message_label.text

    property var sidebar

    /******************************************************/

    RowLayout {
        ToolButton {
            action: Action {
                id: sidebar_open_action
                property bool first_time: true
                checkable: true
                checked: sidebar.opened
                icon.source: checked ? "qrc:/icons/svg/sidebar-collapse-left.svg" : "qrc:/icons/svg/sidebar-expand-left.svg"
                // onTriggered: checked ? sidebar.close() : sidebar.open()
                onTriggered: {
                    if (first_time) {
                        first_time = false
                        sidebar.open()
                    } else {
                        checked ? sidebar.close() : sidebar.open()
                    }
                }
            }
            ToolTip.visible: enabled && hovered
            ToolTip.delay: 2000
            ToolTip.text: "open sidebar"
        }

        Label {
            id: message_label
        }

        /*
        ToolButton {
            action: Action {
                icon.source: "qrc:/pdfviewer/resources/go-up-search.svg"
                shortcut: StandardKey.FindPrevious
                onTriggered: view.searchBack()
            }
            ToolTip.visible: enabled && hovered
            ToolTip.delay: 2000
            ToolTip.text: "find previous"
        }

        TextField {
            id: search_field
            placeholderText: "search"
            Layout.minimumWidth: 150
            Layout.fillWidth: true
            Layout.bottomMargin: 3
            onAccepted: {
                sidebar.open()
                sidebarTabs.setCurrentIndex(0)
            }
            Image {
                visible: search_field.text !== ""
                source: "qrc:/pdfviewer/resources/edit-clear.svg"
                sourceSize.height: search_field.height - 6
                anchors {
                    right: parent.right
                    verticalCenter: parent.verticalCenter
                    margins: 3
                }
                TapHandler {
                    onTapped: search_field.clear()
                }
            }
        }

        ToolButton {
            action: Action {
                icon.source: "qrc:/pdfviewer/resources/go-down-search.svg"
                shortcut: StandardKey.FindNext
                onTriggered: view.searchForward()
            }
            ToolTip.visible: enabled && hovered
            ToolTip.delay: 2000
            ToolTip.text: "find next"
        }

        Label {
            id: status_label
            property size implicitPointSize: doc.pagePointSize(view.currentPage)
            text: "page " + (currentPageSB.value) + " of " + doc.pageCount +
                " scale " + view.renderScale.toFixed(2) +
                " original " + implicitPointSize.width.toFixed(1) + "x" + implicitPointSize.height.toFixed(1) + " pt"
            visible: doc.pageCount > 0
        }
        */
    }
}
