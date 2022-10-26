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

import DatasheetExtractor 1.0
import Widgets 1.0 as Widgets
import '.' 1.0 as Ui

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

            Rectangle {
                id: selection_area
                visible: false
                color: '#aaaaaaff'
                x: 0
                y: 0
                width: 100
                height: 100
                property bool first_time: false
            }

            MouseArea {
                id: mouse_area
                anchors.fill: parent

                hoverEnabled: true

                property int margin: 60
                property int size_min: 100

                property int x_handler: 0
                property int y_handler: 0
                property bool edited: false

                function get_handler(mouse) {
                    var x = mouse.x
                    var y = mouse.y
                    var x_inf = selection_area.x
                    var y_inf = selection_area.y
                    var x_sup = x_inf + selection_area.width
                    var y_sup = y_inf + selection_area.height

                    var _x_handler, _y_handler

                    if (x < (x_inf + margin))
                        _x_handler = 1
                    else if ((x_sup - margin) < x)
                        _x_handler = 3
                    else
                        _x_handler = 2

                    if (y < (y_inf + margin))
                        _y_handler = 1
                    else if ((y_sup - margin) < y)
                        _y_handler = 3
                    else
                        _y_handler = 2

                    return {x:_x_handler, y:_y_handler}
                }

                function update_pointer(mouse) {
                    var handler = get_handler(mouse)
                    x_handler = handler.x
                    y_handler = handler.y
                    if (x_handler != 2 || y_handler != 2)
                        cursorShape = Qt.CrossCursor
                    else
                        cursorShape = Qt.ArrowCursor
                }

                function start_selection_area(mouse) {
                    var handler = get_handler(mouse)
                    x_handler = handler.x
                    y_handler = handler.y
                    edited = true
                    console.info('Handlers', x_handler, y_handler)
                }

                function update_selection_area(mouse) {
                    var x = Math.min(Math.max(mouse.x, 0), pdf_page_image.paintedWidth)
                    var y = Math.min(Math.max(mouse.y, 0), pdf_page_image.paintedHeight)
                    var x_inf = selection_area.x
                    var y_inf = selection_area.y

                    //  X   1  2  3
                    //  Y 1 ii xi si
                    //    2 ix xx sx
                    //    3 is xs ss

                    // console.info(x_handler, y_handler, x, y)
                    if (x_handler == 1) {
                        selection_area.width -= x - x_inf
                        // prevent null area, else area is moved
                        if (selection_area.width > size_min)
                            selection_area.x = x
                    } else if (x_handler == 3)
                        selection_area.width = x - x_inf
                    selection_area.width = Math.max(selection_area.width, size_min)

                    if (y_handler == 1) {
                        selection_area.height -= y - y_inf
                        if (selection_area.height > size_min)
                            selection_area.y = y
                    } else if (y_handler == 3)
                        selection_area.height = y - y_inf
                    selection_area.height = Math.max(selection_area.height, size_min)
                }

                function stop_selection_area(mouse) {
                    x_handler = 0
                    y_handler = 0
                    dirty_selection_area = true
                    edited = false
                }

                onPressed: {
                    if (selection_area.visible)
                        start_selection_area(mouse)
                    else {
                        selection_area.x = mouse.x
                        selection_area.y = mouse.y
                        selection_area.first_time = true
                    }
                }

                onPositionChanged: {
                    if (selection_area.first_time) {
                        selection_area.width = mouse.x - selection_area.x
                        selection_area.height = mouse.y - selection_area.y
                        selection_area.visible = true
                    } else if (selection_area.visible) {
                        if (edited)
                            update_selection_area(mouse)
                        else
                            update_pointer(mouse)
                    }
                }

                onReleased: {
                    if (selection_area.first_time) {
                        selection_area.width = mouse.x - selection_area.x
                        selection_area.height = mouse.y - selection_area.y
                        selection_area.first_time = false
                    } else if (selection_area.visible)
                        stop_selection_area(mouse)
                }
            }
        }
    }
}
