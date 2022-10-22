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

import DatasheetExtractor 1.0
import Widgets 1.0 as Widgets

RowLayout {
    id: root

    /*******************************************************
     *
     * API
     *
     */

    property var actions
    property var page_viewer
    property var page_viewer_page

    /******************************************************/

    property var pdf: application.pdf

    /******************************************************/

    Widgets.ToolButtonTip {
        icon.name: 'zoom-out-black'
        onClicked: page_viewer.zoom_out()
    }

    Widgets.ToolButtonTip {
        action: actions.fit_to_screen_action
    }

    Widgets.ToolButtonTip {
        action: actions.zoom_full_action
    }

    Widgets.ToolButtonTip {
        icon.name: 'zoom-in-black'
        onClicked: page_viewer.zoom_in()
    }

    Widgets.ToolButtonTip {
        icon.name: 'wrap-text-black'
        tip: qsTr('Continuous Mode')
        checkable: true
        onClicked: page_viewer.toggle_continuous_mode()
    }

    Widgets.ToolButtonTip {
        icon.name: 'first-page-black'
        tip: qsTr('First page')
        onClicked: page_viewer.first_page()
    }

    Widgets.ToolButtonTip {
        action: actions.prev_page_action
        tip: qsTr('Previous page')
    }

    Widgets.ToolButtonTip {
        action: actions.next_page_action
        tip: qsTr('Next page')
    }

    Widgets.ToolButtonTip {
        icon.name: 'last-page-black'
        tip: qsTr('Last page')
        onClicked: page_viewer.last_page()
    }

    SpinBox {
        id: page_number
        editable: true
        from: 1
        to: pdf.number_of_pages
        value: page_viewer.pdf_page ? page_viewer.pdf_page.page_number: 0

        onValueModified: page_viewer.to_page(value)
    }

    Label {
        text: '/' + pdf.number_of_pages
    }

    Widgets.ToolButtonTip {
        icon.name: 'grid-on-black'
        tip: qsTr('Show grid')
        checkable: true
        onClicked: page_viewer_page.toggle_grid()
    }

    /*
    Widgets.ToolButtonTip {
        icon.name: 'subject-black'
        tip: qsTr('Convert to text using OCR engine')
        onClicked: page_viewer_page.convert_to_text()
    }
    */

    Widgets.ToolButtonTip {
        action: actions.open_page_in_external_program_action
        // tip: qsTr('Open in ...')
    }
}
