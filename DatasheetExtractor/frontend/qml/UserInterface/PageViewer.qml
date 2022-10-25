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

import DatasheetExtractor 1.0
import Widgets 1.0 as Widgets

Widgets.ImageViewer {

    /*******************************************************
     *
     * API
     *
     */

    property var pdf_page

    property bool continuous_mode: false

    signal page_changed() // int page_number

    function toggle_continuous_mode() {
        continuous_mode = !continuous_mode
    }

    function first_page() {
        to_page(pdf.first_page_number)
        page_changed()
    }

    function last_page() {
        to_page(pdf.last_page_number)
        page_changed()
    }

    function to_page(page_number) {
        console.info("to_page ", page_number)
        if (pdf.is_valid_page_number(page_number)) {
            console.info('before pdf.page')
            pdf_page = pdf.page(page_number)
            console.info('after pdf.page', pdf_page)
            var path = pdf_page.generate_pixmap()
            // console.info("pixmap ", path)
            image_source = 'image://page_image/' + path
            page_changed()
        }
    }

    function prev_page() {
        to_page(pdf_page.page_number -1)
    }

    function next_page() {
        to_page(pdf_page.page_number +1)
    }

    function open_in_external_program() {
        pdf_page.open_in_external_program(application_settings.external_program)
    }

    /******************************************************/

    id: page_viewer

    property var pdf: application.pdf

    // image_source: pdf_page ? pdf_page.path : ''
    image_source: ''

    Component.onCompleted: {
        pdf.new_page.connect(last_page)
    }

    /*
    onMovementEnded: {
        // Fixme: this simple implementation has issues
        //   It require to start a flick event (a wheel event is not enought)
        //     Need a way to receive a wheel event
        //   It show glitches when the page change
        //     Disable the animation
        if (continuous_mode) {
            if (page_viewer.atYBeginning) {
                prev_page()
                page_viewer.contentY = page_viewer.contentHeight
            }
            else if (page_viewer.atYEnd) {
                next_page()
                page_viewer.contentY = 0
            }
        }
    }
    */
}
