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

    property alias current_page_spinbox: current_page_spinbox

    property var actions
    property var pdf_viewer_page
    property var doc
    property var page_viewer

    /******************************************************/

    // property var pdf: application.pdf

    /******************************************************/

    /*
    Widgets.ToolButtonTip {
        action: Action {
            shortcut: StandardKey.Open
            icon.source: "qrc:/pdfviewer/resources/document-open.svg"
            onTriggered: fileDialog.open()
        }
    }
    */
    
    Widgets.ToolButtonTip {
        action: Action {
            shortcut: StandardKey.ZoomIn
            enabled: page_viewer.renderScale < 10
            icon.name: 'zoom-in-black'
            onTriggered: page_viewer.renderScale *= Math.sqrt(2)
        }
    }
    
    Widgets.ToolButtonTip {
        action: Action {
            shortcut: StandardKey.ZoomOut
            enabled: page_viewer.renderScale > 0.1
            icon.name: 'zoom-out-black'
            onTriggered: page_viewer.renderScale /= Math.sqrt(2)
        }
        // icon.name:
        // onClicked: 
    }

    Widgets.ToolButtonTip {
        action: Action {
            icon.source: "qrc:/icons/svg/zoom-fit-width.svg"
            onTriggered: {
                // Fixme: check
                var item = pdf_viewer_page.contentItem
                console.log('pdf container WxH', item.width, item.height)
                page_viewer.scaleToWidth(item.width, item.height)
            }
        }
    }

    Widgets.ToolButtonTip {
        action: Action {
            icon.source: "qrc:/icons/svg/zoom-fit-best.svg"
            onTriggered: {
                var item = pdf_viewer_page.contentItem
                page_viewer.scaleToPage(item.width, item.height)
            }
        }
    }

    Widgets.ToolButtonTip {
        action: Action {
            shortcut: "Ctrl+0"
            icon.source: "qrc:/icons/svg/zoom-original.svg"
            onTriggered: page_viewer.resetScale()
        }
    }

    Widgets.ToolButtonTip {
        action: Action {
            shortcut: "Ctrl+L"
            // icon.source: "qrc:/icons/svg/rotate-left.svg"
            icon.name: "rotate_left-black"
            onTriggered: page_viewer.pageRotation -= 90
        }
    }

    Widgets.ToolButtonTip {
        action: Action {
            shortcut: "Ctrl+R"
            // icon.source: "qrc:/icons/svg/rotate-right.svg"
            icon.name: "rotate_right-black"
            onTriggered: page_viewer.pageRotation += 90
        }
    }

    Widgets.ToolButtonTip {
        // Navigate in history
        action: Action {
            icon.name: "arrow-back-black"
            enabled: page_viewer.backEnabled
            onTriggered: page_viewer.back()
        }
        // Fixme: check
        ToolTip.visible: enabled && hovered
        ToolTip.delay: 2000
        ToolTip.text: "go back"
    }

    Widgets.ToolButtonTip {
        // Navigate in history
        action: Action {
            icon.name: "arrow-forward-black"
            enabled: page_viewer.forwardEnabled
            onTriggered: page_viewer.forward()
        }
        ToolTip.visible: enabled && hovered
        ToolTip.delay: 2000
        ToolTip.text: "go forward"
    }

    SpinBox {
        id: current_page_spinbox
        from: 1
        to: doc.pageCount
        editable: true
        onValueModified: page_viewer.goToPage(value - 1)
        // Cannot create Shortcut
        /*
        Shortcut {
            sequence: StandardKey.MoveToPreviousPage
            onActivated: page_viewer.goToPage(current_page_spinbox.value - 2)
        }
        Shortcut {
            sequence: StandardKey.MoveToNextPage
            onActivated: page_viewer.goToPage(current_page_spinbox.value)
        }
        */

        Component.onCompleted: {
            page_viewer.onCurrentPageChanged.connect(() => {
                current_page_spinbox.value = page_viewer.currentPage + 1
            })
        }
    }

    Label {
        text: '/' + doc.pageCount
    }

    /*
    Widgets.ToolButtonTip {
        action: Action {
            shortcut: StandardKey.SelectAll
            icon.source: "qrc:/icons/svg/edit-select-all.svg"
            onTriggered: page_viewer.selectAll()
        }
    }

    Widgets.ToolButtonTip {
        action: Action {
            shortcut: StandardKey.Copy
            icon.source: "qrc:/icons/svg/edit-copy.svg"
            enabled: page_viewer.selectedText !== ""
            onTriggered: page_viewer.copySelectionToClipboard()
        }
    }
    */

    /*
    Shortcut {
        sequence: StandardKey.Find
        onActivated: searchField.forceActiveFocus()
    }

    Shortcut {
        sequence: StandardKey.Quit
        onActivated: Qt.quit()
    }
    */
}
