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
        var csv = application.tabula_extractor.csv_table()
        console.log('CSV ', csv)
        textarea.text = csv
        // table_view.model = application.tabula_extractor.table
    }

    Component.onCompleted: {
        application.tabula_extractor.done.connect(on_done)
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
            Controls.CustomButton {
                Layout.preferredHeight: 35
                font.pixelSize: 20
                font.bold: true
                color_label: 'white'
                color_background: Style.color.success

                text: qsTr('Process')

                onClicked: process_page()
            }

            BusyIndicator {
                id: busy_indicator
                width: 128
                height: width
                running: false
            }
        }

        CheckBox {
            id: lattice_checkbox
            checked: false
            text: qsTr("Use ruling lines separating each cell")
        }

        ScrollView {
            // Layout.fillHeight: true
            Layout.fillWidth: true
            height: 300
            TextArea {
                id: textarea
            }
        }

        // Fixme: when headers
        TableView {
            id: table_view
            // Layout.fillHeight: true
            height: 300
            Layout.fillWidth: true
            columnSpacing: 1
            rowSpacing: 1
            // clip: true
            model: application.tabula_extractor.table

            delegate: Rectangle {
                implicitWidth: 150
                implicitHeight: 50
                Text {
                    text: display
                }
            }
        }
    }
}
