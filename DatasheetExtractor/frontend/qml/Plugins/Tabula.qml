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

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import DatasheetExtractor
import Constants
import Controls as Controls
import '.' as Ui

Item {
    id: root

    /*******************************************************
     *
     * API
     *
     */

    // application
    property int page_number
    property var selection_area

    /******************************************************/

    function process_page() {
        // Fixme:
        var bounds_pc = selection_area.bounds_pc()
        console.log('Start processing of page ', page_number)
        busy_indicator.running = true
        application.tabula_extractor.process_page_area(
            page_number,
            bounds_pc.y_inf,
            bounds_pc.x_inf,
            bounds_pc.y_sup,
            bounds_pc.x_sup,
            lattice_checkbox.checked,
        )
    }

    function on_done() {
        console.log('Tabula done')
        busy_indicator.running = false
    }

    Component.onCompleted: {
        // application.tabula_extractor.done.connect(on_done)
        application.tabula_extractor.table_changed.connect(on_done)
    }

    /******************************************************/

    ColumnLayout {
        id: column_layout
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        Label {
            font.pixelSize: 30
            text: "<b>Tabula Plugin</b>"
        }

        RowLayout {
            spacing: 20

            Controls.CustomButton {
                Layout.preferredHeight: 35
                font.pixelSize: 20
                font.bold: true
                color_label: 'white'
                color_background: Style.color.success
                text: qsTr('Process')
                onClicked: process_page()
            }

            Controls.CustomButton {
                Layout.preferredHeight: 30
                font.pixelSize: 20
                font.bold: true
                color_label: 'white'
                color_background: Style.color.primary
                text: qsTr('Save')
                onClicked: application.tabula_extractor.save()
                enabled: textarea.text
            }
        }

        RowLayout {
            spacing: 20

            Label {
                text: "Suffix"
            }

            TextField {
                Layout.preferredWidth: root.width / 2
                onEditingFinished: {
                    application.tabula_extractor.suffix = text
                    if (application.tabula_extractor.suffix !== text) {
                        error_message.text = "Invalid suffix"
                    } else
                        error_message.text = ""
                }
                Component.onCompleted: {
                    text = application.tabula_extractor.suffix
                }
            }

            Label {
                id: error_message
                color: Style.color.danger
            }
        }

        CheckBox {
            id: lattice_checkbox
            checked: false
            text: qsTr("Use ruling lines separating each cell")
        }

        BusyIndicator {
            id: busy_indicator
            Layout.preferredWidth: Math.min(64, root.width / 2)
            Layout.preferredHeight: Layout.preferredWidth
            running: false
            visible: running
        }

        ScrollView {
            // Layout.fillHeight: true
            Layout.fillWidth: true
            Layout.preferredHeight: 200
            TextArea {
                id: textarea
                text: application.tabula_extractor.csv_table
            }
        }

        // Fixme: when headers
        // Fixme: table can be dragged and messed
        TableView {
            id: table_view
            Layout.fillHeight: true
            // height: 300
            Layout.fillWidth: true
            columnSpacing: 1
            rowSpacing: 1
            clip: true
            model: application.tabula_extractor.table
             columnWidthProvider: function (column) { return -1 }

            delegate: Rectangle {
                implicitWidth: text_item.paintedWidth + 10
                implicitHeight: 50
                Text {
                    id: text_item
                    text: display
                }
            }
        }
    }
}
