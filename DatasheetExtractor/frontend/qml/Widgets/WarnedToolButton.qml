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

import '.' 1.0 as Widgets

Widgets.ToolButtonTip {

    /*******************************************************
     *
     * API
     *
     */

    property bool warned: false

    /******************************************************/

    id: button

    SequentialAnimation {
        id: flash_animation
        running: warned

        loops: Animation.Infinite
        alwaysRunToEnd: true

        NumberAnimation {
            target: button
            property: 'opacity'
            from: 1
            to: 0.5
            duration: 300
        }
        NumberAnimation {
            target: button
            property: 'opacity'
            from: 0.5
            to: 1
            duration: 300
        }
    }
}
