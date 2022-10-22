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

// Fixme: reset, validation, entered

import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Layouts 1.11
// import Qt.labs.platform 1.1
import QtQuick.Dialogs

import Widgets 1.0 as Widgets

Row {

    /******************************************************
     *
     * API
     *
     */

    property string path

    /*****************************************************/

    id: root

    function set_path(path) {
        // path is prefixed by file://
        if (typeof path === 'object') {
            var prefix = 'file://'
            path = path.toString()
            if (path.startsWith(prefix))
                path = path.slice(prefix.length, path.length)
        }
        if (path)
	    root.path = path
    }

    /******************************************************
     *
     * Dialogs
     *
     */

    FileDialog {
        // Fixme: we cannot set the current file
	id: file_dialog
	fileMode : FileDialog.OpenFile
	onAccepted: set_path(file)
    }

    /******************************************************/

    Widgets.TextField {
        id: text_field
	width: parent.width - button.width
        text: root.path
        // Fixme: validator
        onEditingFinished: set_path(text)
    }

    ToolButton {
	id: button
	icon.name: 'folder-black'
	onClicked: file_dialog.open() // Fixme: current
    }
}
