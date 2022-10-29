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
import QtQuick.Dialogs
import QtQuick.Layouts
import QtQuick.Pdf

import DatasheetExtractor
import '.' as Widgets

Page {

    /*******************************************************
     *
     * API
     *
     */

    property var pdf_document
    property var page_number: 1

    property alias selection_area: selection_area

    /******************************************************/

    id: root

    function format_pc(x) {
        // x *= 100
        return (x).toFixed(0)
    }

    function on_selection_area_changed() {
        var bounds_px = selection_area.bounds_px()
        var bounds_pc = selection_area.bounds_pc()
        selection_area_px_label.text = '[%1, %2]x[%3, %4] px'
            .arg(bounds_px.x_inf)
            .arg(bounds_px.x_sup)
            .arg(bounds_px.y_inf)
            .arg(bounds_px.y_sup)
        selection_area_pc_label.text = '[%1, %2]x[%3, %4] %'
            .arg(format_pc(bounds_pc.x_inf))
            .arg(format_pc(bounds_pc.x_sup))
            .arg(format_pc(bounds_pc.y_inf))
            .arg(format_pc(bounds_pc.y_sup))
    }

    Component.onCompleted: {
        selection_area.changed.connect(on_selection_area_changed)
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        /*
        RowLayout {
            spacing: 10

            Label {
                text: 'Page:'
            }
            Label {
                id: page_number_label
                text: page_number
            }
        }
        */

        RowLayout {
            spacing: 10

            Label {
                text: 'Selection area:'
            }
            Label {
                id: selection_area_px_label
            }
            Label {
                id: selection_area_pc_label
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: 'white'

            // Fixme: show page border
            // border can be cleared by image
            Rectangle {
                anchors.top: parent.top
                anchors.left: parent.left
                width: pdf_page_image.paintedWidth
                height: pdf_page_image.paintedHeight
                border.color: 'black'
                border.width: 2
            }

            PdfPageImage {
                id: pdf_page_image
                anchors.fill: parent
                fillMode: Image.PreserveAspectFit
                horizontalAlignment: Image.AlignLeft
                verticalAlignment: Image.AlignTop
                document: pdf_document
                // Fixme:
                currentFrame: page_number -1

                SelectionArea {
                    id: selection_area
                    anchors.top: parent.top
                    anchors.left: parent.left
                    width: parent.paintedWidth
                    height: parent.paintedHeight
                }
            }
        }
    }
}
