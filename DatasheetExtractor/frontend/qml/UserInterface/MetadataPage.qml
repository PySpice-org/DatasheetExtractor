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

import QtQml 2.11
import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Layouts 1.11

import DatasheetExtractor 1.0
import Widgets 1.0 as Widgets
import Constants 1.0

Page {

    /*******************************************************
     *
     * API
     *
     */

    property var metadata: application.pdf.metadata

    /******************************************************/

    Component.onCompleted: {
        console.info('Completed Metadata Page')
        init()
    }

    function init() {
        // Fixme: UI — QML binding
        //   if use Binding then
        //      valeus are reset at startup
        //      metadata is updated each time a key is pressed
        path_label.text = metadata.path
        // title_textfield.text = metadata.title
        // authors_textfield.text = metadata.authors
        // publisher_textfield.text = metadata.publisher
        // language_textfield.text = metadata.language
        // number_of_pages_label.text = metadata.number_of_pages
        // year_label.text = metadata.year
        // keywords_textfield.text = metadata.keywords
        // description_textfield.text = metadata.description
        // notes_viewer.html_text = metadata.notes_html
        // notes_viewer.markdown_text = metadata.notes
    }

    /******************************************************/

    id: root

    Item {
        anchors.fill: parent
        anchors.margins: 20

        ColumnLayout {

            Widgets.WarnedToolButton {
                id: save_button
                icon.name: 'save-black'
                size: 64
                tip: qsTr('Save')

                warned: metadata.dirty
                icon.color: warned ? Style.color.danger : Style.color.success

                onClicked: metadata.save()
            }

            ScrollView {
                // Fixme:
                id: container
                Layout.preferredWidth: 800
                Layout.fillHeight: true
                clip: true
                ScrollBar.horizontal.policy: ScrollBar.AsNeeded

                GridLayout {
                    width: container.width
                    columns: 2
                    columnSpacing: 10

                    Label {
                        text: qsTr('Path')
                    }
                    Widgets.TextField {
                        id: path_label
                        Layout.fillWidth: true
                        readOnly: true
                    }

                    Label {
                        text: qsTr('Title')
                    }
                    Widgets.TextField {
                        id: title_textfield
                        Layout.fillWidth: true
                        onEditingFinished: metadata.title = text
                    }
                    // Binding { target: metadata; property: 'title'; value: title_textfield.text }

                    Label {
                        text: qsTr('Authors')
                    }
                    Widgets.TextField {
                        id: authors_textfield
                        Layout.fillWidth: true
                        onEditingFinished: metadata.authors = text
                    }
                    // Binding { target: metadata; property: 'authors'; value: authors_textfield.text }

                    Label {
                        text: qsTr('Publisher')
                    }
                    Widgets.TextField {
                        id: publisher_textfield
                        Layout.fillWidth: true
                        onEditingFinished: metadata.publisher = text
                    }
                    // Binding { target: metadata; property: 'publisher'; value: publisher_textfield.text }

                    Label {
                        text: qsTr('Language')
                    }
                    Widgets.TextField {
                        id: language_textfield
                        Layout.fillWidth: true
                        onEditingFinished: metadata.language = text
                    }
                    // Binding { target: metadata; property: 'language'; value: language_textfield.text }

                    Label {
                        text: qsTr('Number of pages')
                    } 
                    Widgets.TextField {
                        id: number_of_pages_label
                        Layout.fillWidth: true
                        readOnly: true
                    }

                    Label {
                        text: qsTr('Year')
                    }
                    SpinBox {
                        id: year_spinbox
                        from: 0
                        to: 2100
                        editable: true
                        // Redefine textFromValue else it shows '2 019'
                        textFromValue: function(value, locale) { return value.toString(); }
                        onValueModified: metadata.year = value
                    }
                    // Binding { target: metadata; property: 'year'; value: year_spinbox.value }

                    Label {
                        text: qsTr('Keywords')
                    }
                    Widgets.TextField {
                        id: keywords_textfield
                        Layout.fillWidth: true
                        onEditingFinished: metadata.keywords = text
                    }
                    // Binding { target: metadata; property: 'keywords'; value: keywords_textfield.text }

                    Label {
                        text: qsTr('Description')
                    }
                    Widgets.TextField {
                        id: description_textfield
                        Layout.fillWidth: true
                        onEditingFinished: metadata.description = text
                    }
                    // Binding { target: metadata; property: 'description'; value: description_textfield.text }


                    Label {
                        text: qsTr('Notes')
                    }
                    Widgets.MarkdownViewer {
                        id: notes_viewer
                        Layout.fillWidth: true
                        Layout.minimumHeight: 200

                        onMarkdown_text_edited: {
                            metadata.notes = markdown_text
                            html_text = metadata.notes_html
                        }
                    }
                }
            }
        }
    }
}
