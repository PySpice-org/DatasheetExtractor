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
        console.log("sidebar y", stack_layout.y)
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
        title: "Error loading " + doc.source
        standardButtons: Dialog.Close
        modal: true
        closePolicy: Popup.CloseOnEscape
        anchors.centerIn: parent
        width: 300
        visible: doc.status === PdfDocument.Error

        contentItem: Label {
            id: errorField
            text: doc.error
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
        onAccepted: doc.password = passwordField.text
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

        function set_library_page() { currentIndex = 0 }
        function set_metadata_page() { currentIndex = 1 }
        function set_thumbnail_page() { currentIndex = 2 }
        function set_viewer_page() { currentIndex = 3 }
        function set_pdf_viewer_page() { currentIndex = 4 }

        Component.onCompleted: {
            console.log("sidebar y", stack_layout.y, pdf_viewer_page.y)
            pdf_viewer_page.sidebar.y = menu_bar.height + header_tool_bar.height
            /*
            if (application.library)
                set_library_page()
            else
                set_thumbnail_page()
            */
            // set_viewer_page()
            // set_pdf_viewer_page()
        }

        // Ui.LibraryPage {
        Item {
            id: library_page
        }

        Ui.MetadataPage {
            id: metadata_page
        }

        // Fixme: simplify with Page { Widget{} } ???
        // Ui.ThumbnailPage {
        Item {
            id: thumbnail_page
            // page_viewer: page_viewer_page.page_viewer
        }

        Ui.PageViewerPage {
            id: page_viewer_page
        }

        Ui.PdfViewerPage {
            id: pdf_viewer_page
            application_window: application_window
            password_dialog: password_dialog
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
