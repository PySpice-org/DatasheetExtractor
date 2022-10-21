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

ApplicationWindow {
    id: application_window

    /*******************************************************
     *
     * API
     *
     */

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
        stack_layout.set_thumbnail_page()
        show_message(qsTr('Loaded pdf at %1'.arg(path)))
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
        page_viewer_page.page_viewer.first_page()
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
    }

    // Widgets.PdfFolderDialog {
    Widgets.NativePdfFolderDialog {
        id: pdf_folder_dialog
        onAccepted: load_pdf(selected_path())
    }

    Ui.OptionsDialog {
        id: options_dialog
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
     * Menu
     *
     */

    // Fixme: use native menu ???
    menuBar: Ui.MenuBar {
        id: menu_bar
        about_dialog: about_dialog
        // Binding loop detected for property
        pdf_folder_dialog: pdf_folder_dialog
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

        Component.onCompleted: {
            /*
            if (application.library)
                set_library_page()
            else
                set_thumbnail_page()
            */
            set_viewer_page()
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
    }

    /*******************************************************
     *
     * Footer
     *
     */

    footer: Ui.FooterToolBar {
        id: footer_tool_bar
    }
}
