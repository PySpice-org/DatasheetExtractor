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

import DatasheetExtractor 1.0

Item {
    id: root

    /*******************************************************
     *
     * API
     *
     */

    property var page_viewer
    // application_window.load_book

    /******************************************************/

    property alias fit_to_screen_action: fit_to_screen_action
    property alias next_page_action: next_page_action
    property alias prev_page_action: prev_page_action
    // property alias reload_action: reload_action
    property alias zoom_full_action:zoom_full_action
    property alias open_page_in_external_program_action:open_page_in_external_program_action

    /******************************************************/

    /*
    Action {
        id: reload_action
        icon.name: 'refresh-black'
        // shortcut: ''
        onTriggered: load_book(application.book.path)
    }
    */

    Action {
        id: prev_page_action
        icon.name: 'arrow-back-black'
        shortcut: application_settings.shortcut('previous_page').sequence
        onTriggered: page_viewer.prev_page()
    }

    Action {
        id: next_page_action
        icon.name: 'arrow-forward-black'
        shortcut: application_settings.shortcut('next_page').sequence
        onTriggered: page_viewer.next_page()
    }

    Action {
        id: fit_to_screen_action
        icon.name: 'settings-overscan-black'
        shortcut: application_settings.shortcut('fit_to_screen').sequence
        onTriggered: page_viewer.fit_to_screen()
    }

    Action {
        id: zoom_full_action // Fixme: name
        icon.name: 'zoom-fit-width'
        shortcut: application_settings.shortcut('full_zoom').sequence
        onTriggered: page_viewer.zoom_full()
    }

    Action {
        id: open_page_in_external_program_action
        icon.name: 'open-in-new-black'
        // shortcut: application_settings.shortcut('open_page_in_external_program').sequence
        onTriggered: page_viewer.open_in_external_program()
    }
}
