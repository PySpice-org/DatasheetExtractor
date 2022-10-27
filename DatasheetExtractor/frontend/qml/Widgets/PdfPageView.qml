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

    property var application_window
    property var pdf_document

    function hide_selection_area() {
        selection_area.visible = false
    }

    function maximise_area() {
        selection_area.x = 0
        selection_area.y = 0
        selection_area.width = pdf_page_image.paintedWidth
        selection_area.height = pdf_page_image.paintedHeight
        selection_area.visible = true
    }

    function bounds() {
        var x_inf = selection_area.x
        var y_inf = selection_area.y
        var x_sup = x_inf + selection_area.width
        var y_sup = y_inf + selection_area.height
        x_inf /= pdf_page_image.paintedWidth
        x_sup /= pdf_page_image.paintedWidth
        y_inf /= pdf_page_image.paintedHeight
        y_sup /= pdf_page_image.paintedHeight
        return {x_inf:x_inf, x_sup:x_sup, y_inf:y_inf, y_sup:y_sup}
    }

    /******************************************************/

    id: root

    Component.onCompleted: {
    }

    Rectangle {
        anchors.fill: parent
        color: 'white'

        PdfPageImage {
            id: pdf_page_image
            // else image is centered
            // anchors.fill: parent
            anchors.margins: 10
            fillMode: Image.PreserveAspectFit
            document: pdf_document
            currentFrame: application_window.header_tool_bar.pdf_viewer_toolbar.current_page_spinbox.value -1

            SelectionArea {
                anchors.fill: parent
            }
        }
    }
}
