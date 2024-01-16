# -*- coding: utf-8 -*-
# This file is a part of PriceMem Program which is GNU GPLv3 licensed
# Copyright (C) 2024 Arindam Chaudhuri <arindamsoft94@gmail.com>
from PyQt5.QtCore import ( Qt, pyqtSignal, QTimer, QRegExp, QModelIndex, QPoint
)
from PyQt5.QtGui import ( QIcon, QRegExpValidator, QIntValidator, QDoubleValidator,
    QStandardItemModel, QStandardItem,
)
from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QGridLayout, QComboBox, QDialogButtonBox,
    QToolButton, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QCompleter, QMessageBox, QMenu
)

from common import App
from file_io import save_purchases_file

from datetime import datetime
import calendar


class NewPurchaseDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setWindowTitle("Add New Purchase")
        self.resize(640,480)
        # create widgets
        self.dateLabel = QLabel("Date", self)
        self.productLabel = QLabel("Product", self)
        self.quantityLabel = QLabel("Quantity", self)
        self.priceLabel = QLabel("Price", self)
        self.dateEdit = DateEdit(self)
        self.dateEdit.setPlaceholderText("DDMMYYYY")
        self.dateEdit.setMaximumWidth(self.dateEdit.height()*3)
        self.productEdit = ProductInput(self)
        self.quantityEdit = QLineEdit(self)
        self.quantityEdit.setValidator(QRegExpValidator(QRegExp("(\d+([.]\d+)?)\D*"), self.quantityEdit))
        self.quantityEdit.setMaximumWidth(self.quantityEdit.height()*2)
        self.priceEdit = QLineEdit(self)
        self.priceEdit.setValidator(QDoubleValidator(0.0, 100000.0, 2, self.priceEdit))
        self.priceEdit.setMaximumWidth(self.priceEdit.height()*2)
        self.addButton = QPushButton("Add", self)
        self.purchaseTable = QTableWidget(self)
        self.purchaseTable.setAlternatingRowColors(True)
        self.purchaseTable.setColumnCount(5)
        self.purchaseTable.setHorizontalHeaderLabels(["Date","Product", "Quantity", "Price", "Sell Price"])
        self.purchaseTable.horizontalHeader().setDefaultSectionSize(80)
        self.purchaseTable.verticalHeader().setDefaultSectionSize(25)
        self.purchaseTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.buttonbox = QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel, Qt.Horizontal, self)
        # this makes pressing Enter adds item, instead of closing dialog
        self.addButton.setDefault(True)
        # add widgets
        self.topLayout = QGridLayout(self)
        self.topLayout.addWidget(self.dateLabel, 0,0,1,1)
        self.topLayout.addWidget(self.productLabel, 0,1,1,1)
        self.topLayout.addWidget(self.quantityLabel, 0,2,1,1)
        self.topLayout.addWidget(self.priceLabel, 0,3,1,1)
        self.topLayout.addWidget(self.dateEdit, 1,0,1,1)
        self.topLayout.addWidget(self.productEdit, 1,1,1,1)
        self.topLayout.addWidget(self.quantityEdit, 1,2,1,1)
        self.topLayout.addWidget(self.priceEdit, 1,3,1,1)
        self.topLayout.addWidget(self.addButton, 1,4,1,1)
        self.topLayout.addWidget(self.purchaseTable, 2,0,1,5)
        self.topLayout.addWidget(self.buttonbox, 3,0,1,5)
        self.topLayout.setColumnStretch(1,1)

        self.buttonbox.accepted.connect(self.accept)
        self.buttonbox.rejected.connect(self.reject)
        self.addButton.clicked.connect(self.addToList)

        self.productEdit.updateData()
        # result
        self.purchases = []

    def addToList(self):
        # get data
        date = self.dateEdit.text()
        if not is_valid_date(date):
            QMessageBox.warning(self, "Invalid Date", "Date is not valid !")
            return
        product = self.productEdit.product
        if not product:
            QMessageBox.warning(self, "Select Product", "Product not selected !")
            return
        quantity = self.quantityEdit.text()
        if not quantity:
            QMessageBox.warning(self, "Quantity Empty", "Quantity is Empty !")
            return
        price = self.priceEdit.text()
        if not price:
            QMessageBox.warning(self, "Price Empty", "Price is Empty !")
            return
        row_data = [date, product[0], get_product_title(product), quantity, price]
        # show data
        row = self.purchaseTable.rowCount()
        self.purchaseTable.insertRow(row)
        for col,val in enumerate(row_data[:1]+row_data[2:]+[product[4]]):
            item = QTableWidgetItem(val)
            self.purchaseTable.setItem(row, col, item)
            if col!=1:
                item.setTextAlignment(Qt.AlignCenter)

        row_data[0] = to_sortable_date(row_data[0])
        self.purchases.append(row_data)
        # clear fields
        self.productEdit.clear()
        self.quantityEdit.clear()
        self.priceEdit.clear()


class ProductInput(QLineEdit):
    def __init__(self, parent):
        QLineEdit.__init__(self, parent)
        self.setStyleSheet("QLineEdit { padding: 2 22 2 2; background: white; border: 1px solid gray; border-radius: 3px;}")
        # Create button for showing page icon
        self.button = QToolButton(self)
        self.button.setStyleSheet("QToolButton { border: 0; background: transparent; width: 16px; height: 16px; }")
        self.button.setCursor(Qt.PointingHandCursor)
        self.button.setIcon(QIcon(':/icons/add.png'))
        self.button.setToolTip("Add New Product")
        self.button.clicked.connect(self.onButtonClick)
        # the completer
        model = QStandardItemModel(self)
        self._completer = QCompleter(model, self)
        self._completer.setFilterMode(Qt.MatchContains)
        self._completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._completer.activated[QModelIndex].connect(self.onSuggestionSelected)
        #self._completer.setCompletionColumn(0)
        self.setCompleter(self._completer)

        self.textEdited.connect(self.onTextEdit)
        self.product = None

    def onTextEdit(self, text):
        # here we can not check for popup visibility.
        # because popup is shown after this function ends.
        QTimer.singleShot(0, self.checkPopup)

    def checkPopup(self):
        has_popup = self.completer().popup().isVisible()
        self.button.setHidden(has_popup)

    def onButtonClick(self):
        """ Add new product """
        product = App.window.addNewProduct()
        if not product:
            return
        self.product = product
        self.updateData()
        self.setText(get_product_title(self.product))

    def onSuggestionSelected(self, index):
        # index.row() returns the index in completionModel, not the original
        # model we have set. it can be obtained using sibling() method
        index = index.sibling(index.row(), 1).data(Qt.DisplayRole)
        self.product = App.products[int(index)]

    def updateData(self):
        model = self._completer.model()
        model.setRowCount(len(App.products))
        model.setColumnCount(2)
        for i, product in enumerate(App.products):
            item = QStandardItem(get_product_title(product))
            model.setItem(i,0, item)
            item = QStandardItem(str(i))
            model.setItem(i,1, item)

    def resizeEvent(self, ev):
        self.button.move(self.width()-22,3)
        QLineEdit.resizeEvent(self, ev)

    def clear(self):
        QLineEdit.clear(self)
        self.product = None


def get_product_title(product):
    """ get title in 'NAME (BRAND)' format """
    s = "%s" % product[1]# name
    s += product[2] and " (%s)"%product[2] or ""# brand
    return s


def is_valid_date(date):
    try:
        datetime.strptime(date, "%d/%m/%Y")
        return True
    except:
        return False


class PurchaseHistoryDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setWindowTitle("Purchase History")
        self.resize(640, 480)

        filterLabel = QLabel("Filter :")
        self.filterCombo = QComboBox(self)
        self.filterCombo.addItems(["1 Month", "6 Months", "1 Year", "Show All", "Date Range"])
        self.fromDateEdit = DateEdit(self)
        self.fromDateEdit.setPlaceholderText("From : DDMMYYYY")
        self.toDateEdit = DateEdit(self)
        self.toDateEdit.setPlaceholderText("To : DDMMYYYY")
        # The Purchase history table
        self.purchaseTable = QTableWidget(self)
        self.purchaseTable.setAlternatingRowColors(True)
        self.purchaseTable.setColumnCount(4)
        self.purchaseTable.setHorizontalHeaderLabels(["Date","Product", "Quantity", "Price"])
        self.purchaseTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.purchaseTable.verticalHeader().setDefaultSectionSize(25)
        self.purchaseTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.purchaseTable.setSelectionBehavior(QTableWidget.SelectRows)

        self.btnBox = QDialogButtonBox(QDialogButtonBox.Close, Qt.Horizontal, self)
        # this prevent closing dialog when pressing Enter in DateEdit
        self.btnBox.button(QDialogButtonBox.Close).setAutoDefault(False)

        self.topLayout = QGridLayout(self)
        self.topLayout.addWidget(filterLabel, 0,0,1,1)
        self.topLayout.addWidget(self.filterCombo, 0,1,1,1)
        self.topLayout.addWidget(self.fromDateEdit, 0,2,1,1)
        self.topLayout.addWidget(self.toDateEdit, 0,3,1,1)
        self.topLayout.addWidget(self.purchaseTable, 1,0,1,5)
        self.topLayout.addWidget(self.btnBox, 2,0,1,5)
        self.topLayout.setColumnStretch(4,1)

        self.filterCombo.currentIndexChanged[str].connect(self.onFilterChange)
        self.fromDateEdit.editingFinished.connect(self.updateTable)
        self.toDateEdit.editingFinished.connect(self.updateTable)
        self.purchaseTable.customContextMenuRequested.connect(self.showTableMenu)
        self.btnBox.accepted.connect(self.accept)
        self.btnBox.rejected.connect(self.reject)

        self.fromDateEdit.setHidden(True)
        self.toDateEdit.setHidden(True)

        self.updateTable()

    def onFilterChange(self, date_filter):
        show_range = date_filter=="Date Range"
        self.fromDateEdit.setVisible(show_range)
        self.toDateEdit.setVisible(show_range)
        self.updateTable()

    def updateTable(self):
        # filter according to dates
        date_filter = self.filterCombo.currentText()
        if date_filter == "Show All":
            purchases = App.purchases
        else:
            today = datetime.today()
            end_date = today.strftime("%Y%m%d")
            if date_filter=="1 Month":
                start_date = monthdelta(today, -1)
            elif date_filter=="6 Months":
                start_date = monthdelta(today, -6)
            elif date_filter=="1 Year":
                start_date = monthdelta(today, -12)
            elif date_filter=="Date Range":
                start_date = self.fromDateEdit.text()
                end_date = self.toDateEdit.text()
                if not is_valid_date(start_date) or not is_valid_date(end_date):
                    return
                start_date = to_sortable_date(start_date)
                end_date = to_sortable_date(end_date)
            purchases = filter(lambda x : start_date<=x[0]<=end_date, App.purchases)
        # sort according to date
        self.purchases = sorted(purchases, key=lambda x : x[0])

        self.purchaseTable.clearContents()
        self.purchaseTable.setRowCount(len(self.purchases))
        for row, row_data in enumerate(self.purchases):
            row_data = [to_readable_date(row_data[0])] + row_data[2:]
            for col, text in enumerate(row_data):
                item = QTableWidgetItem(text)
                self.purchaseTable.setItem(row, col, item)
                if col!=1:
                    item.setTextAlignment(Qt.AlignCenter)

    def showTableMenu(self, pos):
        """ show context menu on table """
        item = self.purchaseTable.itemAt(pos)
        if not item:
            return
        offset = QPoint(self.purchaseTable.verticalHeader().width()+3, self.purchaseTable.horizontalHeader().height()+3)
        menu = QMenu(self.purchaseTable)
        menu.addAction("Delete", self.deleteSelected)
        menu.exec(self.purchaseTable.mapToGlobal(pos+offset))

    def deleteSelected(self):
        """ delete selected items in purchase table"""
        rows = self.purchaseTable.selectionModel().selectedRows()
        selected_rows = [item.row() for item in rows]
        selected_rows.sort(reverse=True)
        for row in selected_rows:
            self.purchaseTable.removeRow(row)
            item = self.purchases.pop(row)
            App.purchases.remove(item)
        self.purchaseTable.clearSelection()
        save_purchases_file()



class DateEdit(QLineEdit):
    """ automatically puts slash between numbers """
    # signals
    dateEntered = pyqtSignal(str)
    # constructor
    def __init__(self, parent):
        QLineEdit.__init__(self, parent)
        # validator for "DD/MM/YYYY" (allows entering DDMMYYYY then converts to DD/MM/YYYY)
        self.setValidator(QRegExpValidator(QRegExp("\d{2}[0-9/]\d{2}[0-9/]\d{4}"), self))

    def keyPressEvent(self, ev):
        # automatically insert / where required
        QLineEdit.keyPressEvent(self, ev)
        text = self.text()
        if len(text) in (3,6) and text[-1]!="/":
            self.setText(text[:-1]+"/"+text[-1])



# equivalent to datetime.strptime(date, "%d/%m/%Y").strftime("%Y%m%d")
def to_sortable_date(date):
    """ convert from human readable DD/MM/YYYY to sortable YYYYMMDD format """
    return date[6:] + date[3:5] + date[:2]

def to_readable_date(date):
    """ convert from sortable YYYYMMDD to human readable DD/MM/YYYY format """
    return "%s/%s/%s" % (date[6:], date[4:6], date[:4])

def monthdelta(date, delta):
    m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
    m = m or 12
    d = min(date.day, calendar.monthrange(y, m)[1])
    return date.replace(day=d,month=m, year=y).strftime("%Y%m%d")



class ProductHistoryDialog(QDialog):
    """ Purchase History of a particular product """
    def __init__(self, product_info, parent):
        QDialog.__init__(self, parent)
        self.product_id = product_info[0]
        self.setWindowTitle("Product Purchase History")
        self.resize(640, 480)

        self.purchaseTable = QTableWidget(self)
        self.purchaseTable.setAlternatingRowColors(True)
        self.purchaseTable.setColumnCount(4)
        self.purchaseTable.setHorizontalHeaderLabels(["Date","Quantity", "Total Price", "Price/Unit"])
        self.purchaseTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.purchaseTable.verticalHeader().setDefaultSectionSize(25)
        self.btnBox = QDialogButtonBox(QDialogButtonBox.Close, Qt.Horizontal, self)

        layout = QGridLayout(self)
        layout.addWidget(self.purchaseTable, 0,0,1,1)
        layout.addWidget(self.btnBox, 1,0,1,1)

        self.btnBox.accepted.connect(self.accept)
        self.btnBox.rejected.connect(self.reject)

        self.updateTable()


    def updateTable(self):
        # filter according to dates
        purchases = App.purchases
        purchases = filter(lambda x : x[1]==self.product_id, App.purchases)
        purchases = sorted(purchases, key=lambda x : x[0])

        self.purchaseTable.setRowCount(len(purchases))

        for row, row_data in enumerate(purchases):
            date, pdt_id, title, quantity, price = row_data
            price_per_unit = "%g" % (float(price)/get_quantity_number(quantity))
            row_data = [to_readable_date(date), quantity, price, price_per_unit]
            for col, text in enumerate(row_data):
                item = QTableWidgetItem(text)
                self.purchaseTable.setItem(row, col, item)
                item.setTextAlignment(Qt.AlignCenter)

import re
# matches 1 or 1kg or 1.0kg or 1.0 kg
quantity_re = re.compile("(\d+([.]\d+)?)\D*")

def get_quantity_number(text):
    """ returns 1.0 from 1.0kg """
    match = quantity_re.match(text)
    if match:
        return float(match.group(1))
    else:
        return 1
