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
import Widgets as Widgets
import '.' as Ui

Page {

    /*******************************************************
     *
     * API
     *
     */

    property var application_window
    property alias pdf_document: page_view.pdf_document

    /******************************************************/

    id: root

    Component.onCompleted: {
    }

    ListModel {
        id: modules

        ListElement {
            title: qsTr('Tabula')
            icon: ''
            // source: 'qrc:/.qml'
        }

        ListElement {
            title: qsTr('Pinout')
            icon: ''
            // source: 'qrc:/.qml'
        }
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

        model: modules

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
            width: parent.width * .2
            height: parent.height
	    spacing: 0
            
            model: delegate_model
            ScrollIndicator.vertical: ScrollIndicator {}
        }

        Widgets.PdfPageView {
            id: page_view
            width: parent.width * .4
            height: parent.height
        }

        Item {
            id: processing_panel
            width: parent.width * .4
            height: parent.height

            RowLayout{
                id: row_layout
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10

                ColumnLayout {
                    id: column_layout
                    Layout.alignment: Qt.AlignTop
                    Layout.preferredWidth: row_layout.width / 3
                    spacing: 20
                    
                    // Controls.CustomButton {
                    Button {
                        Layout.preferredHeight: 30
                        Layout.preferredWidth: column_layout.width
                        font.pixelSize: 20
                        font.bold: true
                        // color_label: 'white'
                        // color_background: Style.color.success
                        
                        text: qsTr('Process')
                        
                        onClicked: {
                            console.log('Start processing...')
                        }
                    }
                }
            }
        }
    }
}
