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

    property alias pdf_document: pdf_document
    property alias page_viewer: page_viewer
    property alias sidebar: sidebar

    property var application_window
    property var password_dialog
    property string pdf_path
    
    /******************************************************/

    id: root

    Component.onCompleted: {
        console.log("sidebar y", sidebar.y, root.y, application_window.stack_layout.y)
    }

    /******************************************************/
  
    PdfDocument {
        id: pdf_document
        source: Qt.resolvedUrl(pdf_path)
        onPasswordRequired: password_dialog.open()
    }

    PdfMultiPageView {
        id: page_viewer  // was view
        anchors.fill: parent
        // anchors.leftMargin: sidebar.position * sidebar.width
        document: pdf_document
        // searchString: search_field.text // on footer
        // onCurrentPageChanged: current_page_spinbox.value = page_viewer.currentPage + 1
    }

    Drawer {
        id: sidebar
        edge: Qt.LeftEdge
        modal: false
        width: 300
        y: application_window.menu_bar.height + application_window.header_tool_bar.height
        height: page_viewer.height
        dim: false
        clip: true

        TabBar {
            id: sidebar_tabs
            x: -width
            rotation: -90
            transformOrigin: Item.TopRight
            currentIndex: 2 // bookmarks by default
            TabButton {
                text: qsTr("Info")
            }
            TabButton {
                text: qsTr("Search Results")
            }
            TabButton {
                text: qsTr("Bookmarks")
            }
            TabButton {
                text: qsTr("Pages")
            }
        }

        GroupBox {
            anchors.fill: parent
            anchors.leftMargin: sidebar_tabs.height

            StackLayout {
                anchors.fill: parent
                currentIndex: sidebar_tabs.currentIndex
                component InfoField: TextInput {
                    width: parent.width
                    selectByMouse: true
                    readOnly: true
                    wrapMode: Text.WordWrap
                }

                Column {
                    spacing: 6
                    width: parent.width - 6
                    Label { font.bold: true; text: qsTr("Title") }
                    InfoField { text: pdf_document.title }
                    Label { font.bold: true; text: qsTr("Author") }
                    InfoField { text: pdf_document.author }
                    Label { font.bold: true; text: qsTr("Subject") }
                    InfoField { text: pdf_document.subject }
                    Label { font.bold: true; text: qsTr("Keywords") }
                    InfoField { text: pdf_document.keywords }
                    Label { font.bold: true; text: qsTr("Producer") }
                    InfoField { text: pdf_document.producer }
                    Label { font.bold: true; text: qsTr("Creator") }
                    InfoField { text: pdf_document.creator }
                    Label { font.bold: true; text: qsTr("Creation date") }
                    InfoField { text: pdf_document.creationDate }
                    Label { font.bold: true; text: qsTr("Modification date") }
                    InfoField { text: pdf_document.modificationDate }
                }

                ListView {
                    id: search_results_list
                    implicitHeight: parent.height
                    model: page_viewer.searchModel
                    currentIndex: page_viewer.searchModel.currentResult
                    ScrollBar.vertical: ScrollBar { }
                    delegate: ItemDelegate {
                        id: result_delegate
                        required property int index
                        required property int page
                        required property string contextBefore
                        required property string contextAfter
                        width: parent ? parent.width : 0
                        RowLayout {
                            anchors.fill: parent
                            spacing: 0
                            Label {
                                text: "Page " + (result_delegate.page + 1) + ": "
                            }
                            Label {
                                text: result_delegate.contextBefore
                                elide: Text.ElideLeft
                                horizontalAlignment: Text.AlignRight
                                Layout.fillWidth: true
                                Layout.preferredWidth: parent.width / 2
                            }
                            Label {
                                font.bold: true
                                text: page_viewer.searchString
                                width: implicitWidth
                            }
                            Label {
                                text: result_delegate.contextAfter
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                                Layout.preferredWidth: parent.width / 2
                            }
                        }
                        highlighted: ListView.isCurrentItem
                        onClicked: page_viewer.searchModel.currentResult = result_delegate.index
                    }
                }

                TreeView {
                    id: bookmarks_tree
                    implicitHeight: parent.height
                    implicitWidth: parent.width
                    columnWidthProvider: function() { return width }
                    delegate: TreeViewDelegate {
                        required property int page
                        required property point location
                        required property real zoom
                        onClicked: page_viewer.goToLocation(page, location, zoom)
                    }
                    model: PdfBookmarkModel {
                        document: pdf_document
                    }
                    ScrollBar.vertical: ScrollBar { }
                }

                GridView {
                    id: thumbnails_view
                    implicitWidth: parent.width
                    implicitHeight: parent.height
                    model: pdf_document.pageModel
                    cellWidth: width / 2
                    cellHeight: cellWidth + 10
                    delegate: Item {
                        required property int index
                        required property string label
                        required property size pointSize
                        width: thumbnails_view.cellWidth
                        height: thumbnails_view.cellHeight
                        Rectangle {
                            id: paper
                            width: image.width
                            height: image.height
                            x: (parent.width - width) / 2
                            y: (parent.height - height - page_number.height) / 2
                            PdfPageImage {
                                id: image
                                document: pdf_document
                                currentFrame: index
                                asynchronous: true
                                fillMode: Image.PreserveAspectFit
                                property bool landscape: pointSize.width > pointSize.height
                                width: landscape ? thumbnails_view.cellWidth - 6
                                    : height * pointSize.width / pointSize.height
                                height: landscape ? width * pointSize.height / pointSize.width
                                    : thumbnails_view.cellHeight - 14
                                sourceSize.width: width
                                sourceSize.height: height
                            }
                        }

                        Text {
                            id: page_number
                            anchors.bottom: parent.bottom
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: label
                        }

                        TapHandler {
                            onTapped: page_viewer.goToPage(index)
                        }
                    }
                }
            }
        }
    }
}
