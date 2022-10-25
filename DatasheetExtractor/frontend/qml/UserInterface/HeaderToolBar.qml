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
import UserInterface 1.0 as Ui

ToolBar {
    id: root

    /*******************************************************
     *
     * API
     *
     */

    property var actions
    property var page_viewer_page
    property var pdf_viewer_page
    property var stack_layout

    /******************************************************/

    RowLayout {
        anchors.fill: parent
        spacing: 10

        RowLayout {
            /*
            Widgets.ToolButtonTip {
                icon.name: 'library-books-black'
                tip: qsTr('Show Book Library')
                onClicked: stack_layout.set_library_page()
            }
            */

            Widgets.ToolButtonTip {
                icon.name: 'edit-black'
                tip: qsTr('Edit metadata')
                onClicked: stack_layout.set_metadata_page()
            }

            /*
            Widgets.ToolButtonTip {
                icon.name: 'view-comfy-black'
                tip: qsTr('Show page thumbnails')
                onClicked: stack_layout.set_thumbnail_page()
            }
            */

            Widgets.ToolButtonTip {
                // icon.name: 'image-black'
                icon.name: 'pageview-black'
                tip: qsTr('Show page viewer')
                onClicked: stack_layout.set_viewer_page()
            }

            Widgets.ToolButtonTip {
                icon.name: 'picture_as_pdf-black'
                tip: qsTr('Show PDF viewer')
                onClicked: stack_layout.set_pdf_viewer_page()
            }
        }

        Ui.PageViewerToolBar {
            visible: page_viewer_page.visible

            // why root. ?
            actions: root.actions
            page_viewer: root.page_viewer_page.page_viewer
            page_viewer_page: root.page_viewer_page
        }

        Ui.PdfViewerToolBar {
            visible: pdf_viewer_page.visible
            // anchors.fill: parent
            // anchors.rightMargin: 6

            actions: root.actions
            pdf_viewer_page: root.pdf_viewer_page
            doc: root.pdf_viewer_page.doc
            page_viewer: root.pdf_viewer_page.page_viewer
        }

        Item {
            Layout.fillWidth: true
        }
    }
}
