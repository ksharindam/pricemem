# -*- coding: utf-8 -*-
# This file is a part of PriceMem Program which is GNU GPLv3 licensed
# Copyright (C) 2024 Arindam Chaudhuri <arindamsoft94@gmail.com>

from PyQt5.QtCore import QTimer, Qt, QRect, QSettings
from PyQt5.QtGui import (QPixmap, QPainter, QPen, QFontMetrics, QFont, QIcon,
    QDoubleValidator, QTransform, QIntValidator
)
from PyQt5.QtWidgets import (QGridLayout, QVBoxLayout, QHBoxLayout, QFormLayout,
    QSizePolicy, QDialog, QDialogButtonBox, QFrame, QGroupBox, QWidget, QScrollArea,
    QLabel, QLineEdit, QPushButton, QCompleter
)
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

from purchase_manager import ProductInput, DateEdit

from datetime import datetime


class InvoiceDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setWindowTitle("Generate Invoice")
        # ---------- Load Settings --------------
        self.settings = QSettings("pricemem", "pricemem", self)
        self.settings.beginGroup("Invoice")
        self.last_invoice_no = int(self.settings.value("LastInvoiceNo", 0))
        win_w = int(self.settings.value("WindowWidth", 960))
        win_h = int(self.settings.value("WindowHeight", 640))
        win_maximized = self.settings.value("WindowMaximized", "false") == "true"
        shop_name = self.settings.value("ShopName", "ARINDAMSOFT COMPANY")
        shop_addr = self.settings.value("ShopAddr", "Kshirgram, Purba Bardhaman")
        shop_contact = self.settings.value("ShopContact", "arindamsoft94@gmail.com")
        self.settings.endGroup()

        self.frame = QFrame(self)
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.frame.setMaximumWidth(300)

        self.frame_1 = QFrame(self.frame)
        self.frame_1.setFrameShape(QFrame.StyledPanel)
        self.invoiceNoEdit = QLineEdit(self.frame_1)
        self.invoiceNoEdit.setValidator(QIntValidator(self.invoiceNoEdit))
        self.dateEdit = DateEdit(self.frame_1)

        self.groupBox = QGroupBox("Customer Details :", self.frame)
        self.customerNameEdit = QLineEdit(self.groupBox)
        self.customerNameEdit.setPlaceholderText("Customer Name")
        self.customerNameEdit.setFocus()
        self.addressEdit = QLineEdit(self.groupBox)
        self.addressEdit.setPlaceholderText("Address")
        self.addressCompleter = QCompleter([shop_addr], self.addressEdit)
        self.addressCompleter.setCaseSensitivity(Qt.CaseInsensitive)
        self.addressEdit.setCompleter(self.addressCompleter)
        self.mobNoEdit = QLineEdit(self.groupBox)
        self.mobNoEdit.setPlaceholderText("Mob. No.")

        self.groupBox_2 = QGroupBox("Add Items :", self.frame)
        self.itemEdit = ProductInput(self.groupBox_2)
        self.itemEdit.button.hide()# hide the add product button
        self.itemEdit.setPlaceholderText("Item Name")
        self.quantityEdit = QLineEdit(self.groupBox_2)
        self.quantityEdit.setPlaceholderText("Quantity")
        self.quantityEdit.setValidator(QDoubleValidator(0.0, 99999.0, 3, self.quantityEdit))
        self.rateEdit = QLineEdit(self.groupBox_2)
        self.rateEdit.setPlaceholderText("Rate")
        self.rateEdit.setValidator(QDoubleValidator(0.0, 99999.0, 2, self.rateEdit))
        self.priceEdit = QLineEdit(self.groupBox_2)
        self.priceEdit.setPlaceholderText("Price")
        self.priceEdit.setValidator(QDoubleValidator(0.0, 99999.0, 2, self.priceEdit))
        self.addItemBtn = QPushButton("Add", self.groupBox_2)

        self.frame_2 = QFrame(self.frame)
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.deliveryChargeEdit = QLineEdit(self.frame_2)
        self.deliveryChargeEdit.setPlaceholderText("Delivery Charge")
        self.deliveryChargeEdit.setValidator(QDoubleValidator(0.0, 9999.0, 2, self.deliveryChargeEdit))
        self.discountEdit = QLineEdit(self.frame_2)
        self.discountEdit.setPlaceholderText("Discount")
        self.discountEdit.setValidator(QDoubleValidator(0.0, 99999.0, 2, self.discountEdit))

        self.frame_3 = QFrame(self.frame)
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.shopSettingsBtn = QPushButton("Shop Settings", self.frame_3)
        self.shopNameLabel = QLabel("Shop Name :", self.frame_3)
        self.shopNameEdit = QLineEdit(self.frame_3)
        self.shopAddrLabel = QLabel("Address :", self.frame_3)
        self.shopAddrEdit = QLineEdit(self.frame_3)
        self.shopContactLabel = QLabel("Contact :", self.frame_3)
        self.shopContactEdit = QLineEdit(self.frame_3)
        self.toggleShopSettingsVisibility()

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        layout = QHBoxLayout(self.scrollAreaWidgetContents)
        layout.setContentsMargins(0, 0, 0, 0)
        self.invoice = Invoice(self.scrollArea)
        self.invoice.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(self.invoice)

        self.buttonWidget = QWidget(self)
        btnLayout = QHBoxLayout(self.buttonWidget)
        btnLayout.setContentsMargins(0, 0, 0, 0)
        self.printBtn = QPushButton(QIcon(":/icons/document-print.png"), "Print", self.buttonWidget)
        self.newBtn = QPushButton(QIcon(":/icons/invoice.png"), "New Invoice", self.buttonWidget)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Close, Qt.Horizontal, self)
        self.buttonBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btnLayout.addStretch()
        btnLayout.addWidget(self.printBtn)
        btnLayout.addWidget(self.newBtn)
        btnLayout.addWidget(self.buttonBox)

        self.formLayout_0 = QFormLayout(self.frame_1)
        self.formLayout_0.addRow("Invoice No. :", self.invoiceNoEdit)
        self.formLayout_0.addRow("Date :", self.dateEdit)

        self.gridLayout_1 = QGridLayout(self.groupBox)
        self.gridLayout_1.addWidget(self.customerNameEdit, 0, 0, 1, 1)
        self.gridLayout_1.addWidget(self.addressEdit, 1, 0, 1, 1)
        self.gridLayout_1.addWidget(self.mobNoEdit, 2, 0, 1, 1)

        self.gridLayout_2 = QGridLayout(self.groupBox_2)
        self.gridLayout_2.addWidget(self.itemEdit, 0, 0, 1, 3)
        self.gridLayout_2.addWidget(self.quantityEdit, 1, 0, 1, 1)
        self.gridLayout_2.addWidget(self.rateEdit, 1, 1, 1, 1)
        self.gridLayout_2.addWidget(self.priceEdit, 1, 2, 1, 1)
        self.gridLayout_2.addWidget(self.addItemBtn, 2, 2, 1, 1)

        self.hboxLayout = QHBoxLayout(self.frame_2)
        self.hboxLayout.addWidget(self.deliveryChargeEdit)
        self.hboxLayout.addWidget(self.discountEdit)

        self.formLayout_3 = QFormLayout(self.frame_3)
        self.formLayout_3.addWidget(self.shopSettingsBtn)
        self.formLayout_3.addRow(self.shopNameLabel, self.shopNameEdit)
        self.formLayout_3.addRow(self.shopAddrLabel, self.shopAddrEdit)
        self.formLayout_3.addRow(self.shopContactLabel, self.shopContactEdit)

        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.addWidget(self.frame_1)
        self.verticalLayout.addWidget(self.groupBox)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.verticalLayout.addWidget(self.frame_2)
        self.verticalLayout.addWidget(self.frame_3)
        self.verticalLayout.addStretch()

        self.gridLayout = QGridLayout(self)
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.scrollArea, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.buttonWidget, 1, 0, 1, 2)

        # set initial values
        self.updateNewInvoiceNo()
        self.dateEdit.setText(datetime.today().strftime("%d/%m/%Y"))
        self.shopNameEdit.setText(shop_name)
        self.shopAddrEdit.setText(shop_addr)
        self.shopContactEdit.setText(shop_contact)

        # --------- Connect Signals ------------

        self.invoiceNoEdit.textChanged.connect(self.updateInvoiceData)
        self.dateEdit.textChanged.connect(self.updateInvoiceData)
        self.customerNameEdit.textChanged.connect(self.updateInvoiceData)
        self.addressEdit.textChanged.connect(self.updateInvoiceData)
        self.mobNoEdit.textChanged.connect(self.updateInvoiceData)
        self.itemEdit.productSelected.connect(self.onProductSelect)
        self.quantityEdit.textEdited.connect(self.onQuantityChange)
        self.rateEdit.textEdited.connect(self.onRateChange)
        self.priceEdit.textEdited.connect(self.onPriceChange)
        self.addItemBtn.clicked.connect(self.addItem)
        self.deliveryChargeEdit.textChanged.connect(self.updateInvoiceData)
        self.discountEdit.textChanged.connect(self.updateInvoiceData)
        self.shopSettingsBtn.clicked.connect(self.toggleShopSettingsVisibility)
        self.shopNameEdit.textChanged.connect(self.updateInvoiceData)
        self.shopAddrEdit.textChanged.connect(self.updateInvoiceData)
        self.shopContactEdit.textChanged.connect(self.updateInvoiceData)
        self.printBtn.clicked.connect(self.printInvoice)
        self.newBtn.clicked.connect(self.newInvoice)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.updateInvoiceData()
        self.itemEdit.updateData()# load auto-completion data
        self.resize(win_w, win_h)
        if win_maximized:
            self.setWindowFlags(Qt.Window)# without this line the maximize does not work
            self.setWindowState(Qt.WindowMaximized)



    def updateInvoiceData(self):
        # shop details
        self.invoice.shop_name = self.shopNameEdit.text()
        self.invoice.shop_addr = self.shopAddrEdit.text()
        self.invoice.shop_contact = self.shopContactEdit.text()
        # invoice no. and date
        invoice_no = self.invoiceNoEdit.text() or 1
        self.invoice.invoice_no = "%06d" % int(invoice_no)
        self.invoice.date = self.dateEdit.text()
        # customer info
        self.invoice.cust_name = self.customerNameEdit.text()
        self.invoice.address = self.addressEdit.text()
        self.invoice.mob_no = self.mobNoEdit.text()
        # delivery charge and discount
        delivery_charge = self.deliveryChargeEdit.text() or 0
        self.invoice.delivery_charge = float(delivery_charge)
        discount = self.discountEdit.text() or 0
        self.invoice.discount = float(discount)
        # update invoice pixmap
        self.invoice.redraw()


    def toggleShopSettingsVisibility(self):
        hide = not self.shopNameEdit.isHidden()# isVisible() does not work
        self.shopNameLabel.setHidden(hide)
        self.shopNameEdit.setHidden(hide)
        self.shopAddrLabel.setHidden(hide)
        self.shopAddrEdit.setHidden(hide)
        self.shopContactLabel.setHidden(hide)
        self.shopContactEdit.setHidden(hide)
        self.shopSettingsBtn.setText("Shop Settings" if hide else "Hide Settings")


    def onProductSelect(self, product):
        self.rateEdit.setText(product[4])

    def onQuantityChange(self, quantity):
        if quantity and self.rateEdit.text():
            price = float(quantity) * float(self.rateEdit.text())
            self.priceEdit.setText("%g"%price)

    def onRateChange(self, rate):
        if rate and self.quantityEdit.text():
            price = float(rate) * float(self.quantityEdit.text())
            self.priceEdit.setText("%g"%price)

    def onPriceChange(self, price):
        if price and self.quantityEdit.text() and float(self.quantityEdit.text())!=0.0:
            rate = float(price) / float(self.quantityEdit.text())
            self.rateEdit.setText("%g" % rate)

    def addItem(self):
        item = self.itemEdit.text()
        quantity = self.quantityEdit.text()
        rate = self.rateEdit.text()
        price = self.priceEdit.text()
        if not item or not quantity or not rate or not price:
            return
        self.invoice.addItem([item, quantity, "%.2f"%float(rate), "%.2f"%float(price)])
        self.clearAddItemsWidget()
        self.invoice.redraw()

    def clearAddItemsWidget(self):
        self.itemEdit.clear()
        self.quantityEdit.clear()
        self.rateEdit.clear()
        self.priceEdit.clear()

    def newInvoice(self):
        self.updateNewInvoiceNo()
        self.customerNameEdit.clear()
        self.mobNoEdit.clear()
        self.clearAddItemsWidget()
        self.deliveryChargeEdit.clear()
        self.discountEdit.clear()
        self.invoice.redraw()

    def updateNewInvoiceNo(self):
        self.invoiceNoEdit.setText("%06d" % (self.last_invoice_no+1))

    def printInvoice(self):
        printer = QPrinter(QPrinter.HighResolution)
        dlg = QPrintDialog(printer, self)
        # disable some options (PrintSelection, PrintCurrentPage are disabled by default)
        dlg.setOption(QPrintDialog.PrintPageRange, False)
        dlg.setOption(QPrintDialog.PrintCollateCopies, False)
        if dlg.exec() == QDialog.Accepted:
            painter = QPainter(printer)
            rect = painter.viewport()# area inside margin
            # input page size @ printer dpi
            page_w_px = int(self.invoice.page_size[0]*printer.physicalDpiX()/72)
            page_h_px = int(self.invoice.page_size[1]*printer.physicalDpiY()/72)
            scale = rect.height()/page_h_px
            transform = QTransform.fromScale(scale, scale)
            #transform.translate(rect.x(), rect.y())
            painter.setTransform(transform)
            self.invoice.drawOnPainter(painter, page_w_px, page_h_px)
            painter.end()
            invoice_no = self.invoiceNoEdit.text()
            if invoice_no and int(invoice_no) > self.last_invoice_no:
                self.last_invoice_no = int(invoice_no)


    def done(self, val):
        self.settings = QSettings("pricemem", "pricemem", self)
        self.settings.beginGroup("Invoice")
        self.settings.setValue("LastInvoiceNo", self.last_invoice_no)
        if not self.isMaximized():
            self.settings.setValue("WindowWidth", self.width())
            self.settings.setValue("WindowHeight", self.height())
        self.settings.setValue("WindowMaximized", self.isMaximized())
        self.settings.setValue("ShopName", self.shopNameEdit.text())
        self.settings.setValue("ShopAddr", self.shopAddrEdit.text())
        self.settings.setValue("ShopContact", self.shopContactEdit.text())
        self.settings.endGroup()
        QDialog.done(self, val)



class Invoice(QLabel):
    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # page format
        self.setPageSize(421,595) # calculates page_w and  page_h
        # data
        self.shop_name = ""
        self.shop_addr = ""
        self.shop_contact = ""

        self.invoice_no = ""
        self.date = ""
        self.cust_name = ""
        self.address = ""
        self.mob_no = ""
        self.item_list = []# all item data are str
        self.max_item = 15
        self.delivery_charge = 0
        self.discount = 0

    def setPageSize(self, w, h):
        self.page_size = w, h
        dpi = max(self.physicalDpiX(), self.physicalDpiY())
        self.page_w = int(w*dpi/72)
        self.page_h = int(h*dpi/72)
        #print(self.logicalDpiX(),self.physicalDpiX())

    def addItem(self, item):
        if len(self.item_list)<self.max_item:
            self.item_list.append(item)

    def redraw(self):
        pm = QPixmap(self.page_w, self.page_h)
        pm.fill(Qt.white)

        painter = QPainter(pm)
        self.drawOnPainter(painter, pm.width(), pm.height())
        painter.end()
        self.setPixmap(pm)

    def drawOnPainter(self, painter, page_w, page_h):
        font_family = painter.font().family()
        h1_font = QFont(font_family, 20, QFont.Bold)
        h2_font = QFont(font_family, 12, QFont.Bold)
        h3_font = QFont(font_family, 9.5, QFont.Bold)
        normal_font = QFont(font_family, 10)
        data_font = QFont(font_family, 8)

        painter.setPen(QPen(Qt.CustomDashLine))

        line_top = page_h*1/30

        painter.setFont(normal_font)
        line_height = QFontMetrics(normal_font, painter.device()).height()
        rect = QRect(0, line_top, page_w*20/21, line_height)
        painter.drawText(rect, Qt.AlignRight, "Date : " + self.date)

        rect = QRect(page_w*1/21, line_top, page_w, line_height)
        painter.drawText(rect, Qt.AlignLeft, "Invoice No : " + self.invoice_no)

        painter.setFont(h2_font)
        line_height = QFontMetrics(h2_font, painter.device()).height()
        rect = QRect(0, line_top, page_w, line_height)
        painter.drawText(rect, Qt.AlignHCenter, "INVOICE")
        line_top += 1.5*line_height

        # Write shop name
        while QFontMetrics(h1_font, painter.device()).width(self.shop_name) > page_w*19/21:
            h1_font.setPointSize(h1_font.pointSize()-2)

        painter.setFont(h1_font)
        line_height = QFontMetrics(h1_font, painter.device()).height()
        shop_name_rect = QRect(0, line_top, page_w, line_height)
        painter.drawText(shop_name_rect, Qt.AlignHCenter, self.shop_name)
        line_top += 1.2*line_height

        # Write Shop Address
        painter.setFont(normal_font)
        line_height = QFontMetrics(normal_font, painter.device()).height()
        shop_addr_rect = QRect(0, line_top, page_w, line_height)
        painter.drawText(shop_addr_rect, Qt.AlignHCenter, self.shop_addr)
        line_top += 1.2*line_height

        # Write shop contact info
        shop_contact_rect = QRect(0, line_top, page_w, line_height)
        painter.drawText(shop_contact_rect, Qt.AlignHCenter, self.shop_contact)
        line_top += 2*line_height

        painter.setFont(h3_font)
        font_metrics = QFontMetrics(h3_font, painter.device())
        line_height = font_metrics.height()
        rect = QRect(page_w*1/21, line_top, page_w, line_height)
        painter.drawText(rect, Qt.AlignLeft, "Customer Name :")
        cust_name_rect = rect.adjusted(font_metrics.width("Customer Name :  "),0,0,0)

        rect = QRect(page_w*15/21, line_top, page_w*6/21, line_height)
        painter.drawText(rect, Qt.AlignLeft, "Mob. :")
        mob_no_rect = rect.adjusted(font_metrics.width("Mob. :  "),0,0,0)
        line_top += 1.5*line_height

        rect = QRect(page_w*1/21, line_top, page_w, line_height)
        painter.drawText(rect, Qt.AlignLeft, "Address :")
        address_rect = rect.adjusted(font_metrics.width("Address :  "),0,0,0)
        line_top += 3*line_height

        # Draw Table
        table_w = page_w * 19/21
        table_h = page_h * 0.6
        row_count = self.max_item+4 # including header and 3 footer rows
        row_height = table_h/row_count
        table_top = page_h*0.27
        table_bottom = table_top + row_count*row_height
        table_left = page_w*1/21
        table_right = page_w*20/21

        # initialize table properties
        table_pos = (table_left, table_top)
        lines = (0,0.06,0.68,0.78,0.88,1)
        column_x = [table_left+x*table_w for x in lines[:-1]]
        column_w = [(lines[i+1]-x)*table_w for i,x in enumerate(lines[:-1])]

        for i in range(row_count+1):
            y = table_top + i*row_height
            painter.drawLine(table_left, y, table_right, y)

        for k in (0,0.68,0.88,1):
            x = table_left + k*table_w
            painter.drawLine(x, table_top, x, table_bottom)
        for k in (0.06,0.78):
            x = table_left + k*table_w
            bottom = table_top + (row_count-3)*row_height
            painter.drawLine(x, table_top, x, bottom)

        getCellRect = lambda row, col : QRect(column_x[col],table_pos[1]+row*row_height, column_w[col],row_height)

        for j,text in enumerate(["#", "Item", "Qty", "Rate", "Price"]):
            painter.drawText(getCellRect(0,j), Qt.AlignCenter, text)

        for i, text in enumerate(["Delivery Chg.", "Discount", "Total (Rs.)"]):
            rect = getCellRect(row_count-3+i,2)
            painter.drawText(rect.adjusted(0,0,rect.width(),0), Qt.AlignCenter, text)

        painter.setFont(h3_font)
        line_height = QFontMetrics(h3_font, painter.device()).height()
        line_top = table_bottom + 3*line_height
        rect = QRect(0.65*page_w,line_top, 0.35*page_w, line_height)
        painter.drawText(rect, Qt.AlignCenter, "Signature")
        line_top += 2*line_height

        painter.setFont(normal_font)
        line_height = QFontMetrics(normal_font, painter.device()).height()
        rect = QRect(0, line_top, page_w, line_height)
        painter.drawText(rect, Qt.AlignHCenter, "---------- Thank You ---------")

        # ---------------------- FILL DATA ------------------------
        painter.setFont(data_font)

        painter.drawText(cust_name_rect, Qt.AlignLeft, self.cust_name)
        painter.drawText(mob_no_rect, Qt.AlignLeft, self.mob_no)
        painter.drawText(address_rect, Qt.AlignLeft, self.address)
        # fill table
        total = 0
        for i, item in enumerate(self.item_list):
            painter.drawText(getCellRect(i+1,0), Qt.AlignCenter, str(i+1))
            for j, text in enumerate(item):
                if j==0:
                    painter.drawText(getCellRect(i+1,j+1), Qt.AlignLeft|Qt.AlignVCenter, " "+text)# space is used for padding
                elif j==1:
                    painter.drawText(getCellRect(i+1,j+1), Qt.AlignCenter, text)
                else:
                    painter.drawText(getCellRect(i+1,j+1), Qt.AlignRight|Qt.AlignVCenter, text)
            total += float(item[-1])


        if self.item_list:
            painter.drawText(getCellRect(row_count-3,4), Qt.AlignRight|Qt.AlignVCenter,
                            "%.2f"%self.delivery_charge)
            total += float(self.delivery_charge)
            painter.drawText(getCellRect(row_count-2,4), Qt.AlignRight|Qt.AlignVCenter,
                            "%.2f"%self.discount)
            total -= float(self.discount)
            painter.drawText(getCellRect(row_count-1,4), Qt.AlignRight|Qt.AlignVCenter, "%.2f"%total)
