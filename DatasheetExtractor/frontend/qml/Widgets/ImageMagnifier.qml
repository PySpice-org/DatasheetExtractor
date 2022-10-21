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
import QtQuick.Shapes 1.11

Item {

    /******************************************************
     *
     * API
     *
     */

    // Must be an Image item and has a mouse_area property
    property Item image_viewer: null
    property int pixel_scale: 4

    /******************************************************/

    id: root
    visible: image_viewer != null

    Image {
        id: image_source
        source: image_viewer.source
    }

    ShaderEffectSource {
        id: effect_source
        anchors.fill: parent
        hideSource: true
        visible: false
        smooth: false
        sourceItem: image_source
    }

    ShaderEffect {
        id: effect
        anchors.fill: parent
        property real scaling: effect.width / (pixel_scale * image_source.width) // < 1 for zoom in
        property variant translation // in [0, 1]
        property variant texture: effect_source

        Component.onCompleted: {
            translation: Qt.point(0.0, 0.0)
        }

        function _set_center(mouse) {
            // Image must be top-left aligned in the previewer
            // since mouse area is larger
            var offset = scaling / 2
            var x = mouse.x / image_viewer.paintedWidth - offset
            var y = mouse.y / image_viewer.paintedHeight - offset
            translation = Qt.point(x, y)
        }

        vertexShader: "
            uniform highp mat4 qt_Matrix;
            uniform mediump float scaling;
            uniform mediump vec2 translation;
            attribute highp vec4 qt_Vertex;
            attribute mediump vec2 qt_MultiTexCoord0;
            varying mediump vec2 texCoord;
            varying mediump float on_center;
            void main() {
                texCoord = qt_MultiTexCoord0 * vec2(scaling) + translation;
                gl_Position = qt_Matrix * qt_Vertex;
            }"
        fragmentShader: "
            uniform sampler2D texture;
            uniform lowp float qt_Opacity;
            varying mediump vec2 texCoord;
            void main() {
                gl_FragColor = texture2D(texture, texCoord) * qt_Opacity;
            }"
    }

    property int stroke_width: 3
    property color stroke_color: '#222222'

    Shape {
        id: shape
        anchors.fill: parent

        ShapePath {
            strokeWidth: stroke_width
            strokeColor: stroke_color

            startX: shape.width / 2
            startY: 0
            PathLine { relativeX: 0; relativeY: shape.height }
        }

        ShapePath {
            strokeWidth: stroke_width
            strokeColor: stroke_color

            startX: 0
            startY: shape.height / 2
            PathLine { relativeX: shape.width; relativeY: 0 }
        }
    }

    Connections {
        target: image_viewer != null ? image_viewer.mouse_area : null

        onPressed: {
            if (target.pressedButtons & Qt.LeftButton)
                effect._set_center(mouse)
        }

        onPositionChanged: {
            if (target.pressedButtons & Qt.LeftButton)
                effect._set_center(mouse)
        }
    }
}
