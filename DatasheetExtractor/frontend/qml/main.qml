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
import QtQuick.Layouts

import DatasheetExtractor 1.0
import Widgets 1.0 as Widgets
import UserInterface 1.0 as Ui

ApplicationWindow {
    id: application_window

    /*******************************************************
     *
     * API
     *
     */

    property alias header_tool_bar: header_tool_bar
    property alias stack_layout: stack_layout

    property var shortcuts: null

    function close_application(close) {
        console.info('Close application')
        show_message(qsTr('Close ...'))
        if (!close)
            Qt.quit()
        // else
        //    close.accepted = false
    }

    function clear_message() {
        footer_tool_bar.message = ''
    }

    function show_message(message) {
        footer_tool_bar.message = message
    }

    function load_pdf(path) {
        application.load_pdf(path)
        show_message(qsTr('Loaded PDF %1'.arg(path)))
        
        // stack_layout.set_viewer_page()
        // page_viewer_page.page_viewer.first_page()

        stack_layout.set_pdf_viewer_page()
        pdf_viewer_page.pdf_path = path
    }

    /*******************************************************
     *
     *
     */

    title: qsTr('Datasheet Extractor') // Fixme: ???
    visible: true
    width: 1000
    height: 500

    Component.onCompleted: {
        console.info('ApplicationWindow.onCompleted')
        console.info(application.pdf)
        application.show_message.connect(on_message)
        application.show_error.connect(on_error)
        application_window.showMaximized()
        application.pdf_at_startup.connect(load_pdf)
    }

    function on_message(message) {
        error_message_dialog.open_with_message(message)
    }

    function on_error(message, backtrace) {
        var text = message + '\n' + backtrace
        error_message_dialog.open_with_message(text)
    }

    /*******************************************************
     *
     * Slots
     *
     */

    onClosing: close_application(close)

    /*******************************************************
     *
     * Dialogs
     *
     */

    Widgets.AboutDialog {
        id: about_dialog
        title: qsTr('About Datasheet Extractor')
        about_message: application.about_message // qsTr('...')
    }

    Widgets.ErrorMessageDialog {
        id: error_message_dialog
        title: qsTr('An error occurred in the application')

        /*
        id: errorDialog
        title: "Error loading " + pdf_document.source
        standardButtons: Dialog.Close
        modal: true
        closePolicy: Popup.CloseOnEscape
        anchors.centerIn: parent
        width: 300
        visible: pdf_document.status === PdfDocument.Error

        contentItem: Label {
            id: errorField
            text: pdf_document.error
        }
        */
    }

    // Widgets.PdfFolderDialog {
    Widgets.NativePdfFileDialog {
        id: pdf_file_dialog
        onAccepted: load_pdf(selected_path())
    }

    Ui.OptionsDialog {
        id: options_dialog
    }

    Dialog {
        id: password_dialog
        title: "Password"
        standardButtons: Dialog.Ok | Dialog.Cancel
        modal: true
        closePolicy: Popup.CloseOnEscape
        anchors.centerIn: parent
        width: 300

        contentItem: TextField {
            id: passwordField
            placeholderText: qsTr("Please provide the password")
            echoMode: TextInput.Password
            width: parent.width
            onAccepted: passwordDialog.accept()
        }
        onOpened: passwordField.forceActiveFocus()
        onAccepted: pdf_document.password = passwordField.text
    }

    /*******************************************************
     *
     * Actions
     *
     */

    Ui.Actions {
        id: actions
        page_viewer: page_viewer_page.page_viewer
    }

    /*******************************************************
     *
     * File Drop
     *
     */

    DropArea {
        anchors.fill: parent
        keys: ["text/uri-list"]
        onEntered: (drag) => {
            drag.accepted = (drag.proposedAction === Qt.MoveAction || drag.proposedAction === Qt.CopyAction) &&
                drag.hasUrls && drag.urls[0].endsWith("pdf")
        }
        onDropped: (drop) => {
            load_pdf(drop.urls[0])
            drop.acceptProposedAction()
        }
    }

    /*******************************************************
     *
     * Menu
     *
     */

    // Fixme: use native menu ???
    menuBar: Ui.MenuBar {
        id: menu_bar
        about_dialog: about_dialog
        // Binding loop detected for property
        pdf_file_dialog: pdf_file_dialog
        // Binding loop detected for property
        options_dialog: options_dialog
    }

    /*******************************************************
     *
     * Header
     *
     */

    header: Ui.HeaderToolBar {
        id: header_tool_bar
        actions: actions
        page_viewer_page: page_viewer_page
        pdf_viewer_page: pdf_viewer_page
        stack_layout: stack_layout
    }

    /*******************************************************
     *
     * Items
     *
     */

    StackLayout {
        id: stack_layout
        anchors.fill: parent

        // enum ApplicationPage {
        //     MetadataPage,
        //     ThumbnailPage,
        //     ViewerPage,
        // }

        property var page_map: ({}) // () for QML else it is undefined

        function set_page(page_name) { currentIndex = page_map[page_name] }
        function set_library_page() { currentIndex = page_map.library_page }
        function set_metadata_page() { currentIndex = page_map.metadata_page }
        function set_thumbnail_page() { currentIndex = page_map.thumbnail_page }
        function set_viewer_page() { currentIndex = page_map.page_viewer_page }
        function set_pdf_viewer_page() { currentIndex = page_map.pdf_viewer_page }
        function set_processing_page() { currentIndex = page_map.processing_page }

        function for_each_child(func) {
            for (var i = 0; i < children.length; i++) {
                func(i, children[i])
            }
        }

        Component.onCompleted: {
            // fill page map
            for_each_child((i, page) => {
                page_map[page.id_name] = i
            })

            pdf_viewer_page.sidebar.y = menu_bar.height + header_tool_bar.height
            // set_viewer_page()
            // set_pdf_viewer_page()
        }

        // Fixme: simplify with Page { Widget{} } ???

        /*
         Ui.LibraryPage {
            id: library_page
            property string id_name: 'library_page'
        }
        */

        Ui.MetadataPage {
            id: metadata_page
            property string id_name: 'metadata_page'
        }

        /*
        Ui.ThumbnailPage {
            id: thumbnail_page
            property string id_name: 'thumbnail_page'
        }
        */

        Ui.PageViewerPage {
            id: page_viewer_page
            property string id_name: 'page_viewer_page'
        }

        Ui.PdfViewerPage {
            id: pdf_viewer_page
            application_window: application_window
            password_dialog: password_dialog
            property string id_name: 'pdf_viewer_page'
        }

        Ui.ProcessingPage {
            id: processing_page
            application_window: application_window
            pdf_document: pdf_viewer_page.pdf_document
            property string id_name: 'processing_page'
        }
    }

    /*******************************************************
     *
     * Footer
     *
     */

    footer: Ui.FooterToolBar {
        id: footer_tool_bar
        sidebar: pdf_viewer_page.sidebar
    }
}
