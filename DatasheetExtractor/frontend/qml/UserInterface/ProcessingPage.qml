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
import Constants
import Controls as Controls
import Plugins as Plugins
import Widgets as Widgets
import '.' as Ui

Page {
    id: root

    /*******************************************************
     *
     * API
     *
     */

    property var application_window
    property alias pdf_document: page_view.pdf_document

    property int page_number: 1

    /******************************************************/

    Component.onCompleted: {
        application_window.page_number_changed.connect((page_number) => {
            root.page_number = page_number
        })
    }

    DelegateModel{
        id: delegate_model

        delegate: ItemDelegate {
	    id: control // item_menu_delegate
            width: parent.width
            font.pixelSize: Style.font_size.large
            text: model.title
	    // Try to get a smaller spacing
	    topPadding: 0
	    bottomPadding: 0
	    contentItem: Row {
		spacing: Style.spacing.base_horizontal
                /*
 		Image {
		    anchors.verticalCenter: parent.verticalCenter
		    source: model.icon
		}
                */
		Label {
		    text: control.text
		    font: control.font
		    anchors.verticalCenter: parent.verticalCenter
		}
	    }
            onClicked: {}
        }

        model: Plugins.PluginList {}

        /*
        groups: [
            DelegateModelGroup {
                includeByDefault: false
                name: 'enabled'
            }
        ]
        filterOnGroup: 'enabled'
        */

        // Component.onCompleted: {}
    }

    Row {
        anchors.fill: parent

        ListView {
            id: list_view
            // currentIndex: -1
            width: 200 // parent.width * .2
            height: parent.height
	    spacing: 0

            model: delegate_model
            ScrollIndicator.vertical: ScrollIndicator {}
        }

        Widgets.PdfPageView {
            id: page_view
            width: parent.width * .4
            height: parent.height
            page_number: root.page_number
        }

        Item {
            id: processing_panel
            width: parent.width - page_view.width - list_view.width
            height: parent.height

            Plugins.Tabula {
                anchors.fill: parent
                page_number: root.page_number
                selection_area: page_view.selection_area
            }
        }
    }
}
