
import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts
import QtQuick.Pdf

Item {
    id: pdf_viewer_page
    anchors.fill: parent

    property string pdf_path
    
    PdfDocument {
        id: doc
        source: Qt.resolvedUrl(pdf_path)
        onPasswordRequired: passwordDialog.open()
    }

    PdfMultiPageView {
        id: view
        anchors.fill: parent
        // anchors.leftMargin: sidebar.position * sidebar.width
        document: doc
        // searchString: searchField.text
        // onCurrentPageChanged: currentPageSB.value = view.currentPage + 1
    }
}
