#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This file is a part of PriceMem Program which is GNU GPLv3 licensed
# Copyright (C) 2024 Arindam Chaudhuri <arindamsoft94@gmail.com>

import sys, os

sys.path.append(os.path.dirname(__file__)) # for enabling python 2 like import

from __init__ import __version__, COPYRIGHT_YEAR, AUTHOR_NAME, AUTHOR_EMAIL


from PyQt5.QtCore import ( Qt, qVersion, pyqtSignal, QSettings,
    QStandardPaths, QSize, QPoint
)
from PyQt5.QtGui import ( QIcon, QPixmap, QImage, QPainter,
)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStatusBar, QGridLayout, QWidget,
    QLineEdit, QScrollArea, QDialog, QComboBox, QDialogButtonBox, QLabel, QToolButton,
    QMenu, QHBoxLayout, QVBoxLayout, QStyleOption, QStyle, QSizePolicy, QFileDialog,
    QMessageBox, QCheckBox
)

import resources_rc
from purchase_manager import NewPurchaseDialog, PurchaseHistoryDialog, ProductHistoryDialog
from common import App
from file_io import *

#import platform


categories = ["Electronics", "Electricals", "Grocery", "Hardware",
        "Mobile Accessories", "Stationary", "Services"]


class Window(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("PriceMem - " + __version__)
        self.setWindowIcon(QIcon(":/icons/pricemem.png"))

        self.setupUi()

        # Load settings and Show Window
        self.settings = QSettings("pricemem", "pricemem", self)
        width = int(self.settings.value("WindowWidth", 640))
        height = int(self.settings.value("WindowHeight", 480))
        maximized = self.settings.value("WindowMaximized", "false") == "true"
        App.last_product_id = self.settings.value("LastProdID", App.last_product_id)

        # show window
        self.resize(width, height)
        if maximized:
            self.showMaximized()
        else:
            self.show()

        App.product_icon = QImage(64,64, QImage.Format_RGB32)
        App.product_icon.fill(Qt.white)
        painter = QPainter(App.product_icon)
        painter.drawImage(0,0, QImage(":/icons/pricemem.png"))
        painter.end()
        self.productsContainer = None

        App.products = read_products_file()
        self.showProductList(App.products)
        App.purchases = read_purchases_file()


    def setupUi(self):
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)

        # create main menu
        menu = QMenu(self)
        menu.addAction(QIcon(":/icons/edit-clear.png"), "Clear Database", self.clearData)
        menu.addAction(QIcon(":/icons/help-about.png"), "About", self.showAbout)
        # Menu Button
        menuBtn = QToolButton(self.centralwidget)
        menuBtn.setIcon(QIcon(":/icons/menu.png"))
        menuBtn.setIconSize(QSize(22,22))
        menuBtn.setToolTip("Main Menu")
        menuBtn.setMenu(menu)
        menuBtn.setPopupMode(QToolButton.InstantPopup)
        # New Product Button
        addProductBtn = QToolButton(self.centralwidget)
        addProductBtn.setIcon(QIcon(":/icons/add-item.png"))
        addProductBtn.setIconSize(QSize(22,22))
        addProductBtn.setToolTip("Add New Product")
        # New Purchase Button
        addPurchaseBtn = QToolButton(self.centralwidget)
        addPurchaseBtn.setIcon(QIcon(":/icons/cart.png"))
        addPurchaseBtn.setIconSize(QSize(22,22))
        addPurchaseBtn.setToolTip("Add New Purchase")
        # Purchase History Button
        purchaseHistoryBtn = QToolButton(self.centralwidget)
        purchaseHistoryBtn.setIcon(QIcon(":/icons/order-history.png"))
        purchaseHistoryBtn.setIconSize(QSize(22,22))
        purchaseHistoryBtn.setToolTip("Purchase History")
        # Quit Button
        quitBtn = QToolButton(self.centralwidget)
        quitBtn.setIcon(QIcon(":/icons/quit.png"))
        quitBtn.setIconSize(QSize(22,22))
        quitBtn.setToolTip("Quit")

        searchbar = SearchBar(self.centralwidget)

        self.scrollArea = QScrollArea(self.centralwidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidget = QWidget(self.scrollArea)
        self.scrollArea.setWidget(self.scrollAreaWidget)
        self.scrollAreaLayout = QHBoxLayout(self.scrollAreaWidget)

        # add buttons and searchbar to toolbar layout
        self.toolbarLayout = QHBoxLayout()
        self.toolbarLayout.addWidget(menuBtn)
        self.toolbarLayout.addWidget(addProductBtn)
        self.toolbarLayout.addWidget(addPurchaseBtn)
        self.toolbarLayout.addWidget(purchaseHistoryBtn)
        self.toolbarLayout.addWidget(searchbar)
        self.toolbarLayout.addWidget(quitBtn)
        # add other layout  and widgets to main layout
        self.layout = QGridLayout(self.centralwidget)
        self.layout.addLayout(self.toolbarLayout, 0,0,1,1)
        self.layout.addWidget(self.scrollArea, 1,0,1,1)

        searchbar.searchRequested.connect(self.search)
        addProductBtn.clicked.connect(self.addNewProduct)
        addPurchaseBtn.clicked.connect(self.addNewPurchase)
        purchaseHistoryBtn.clicked.connect(self.showPurchaseHistory)
        quitBtn.clicked.connect(self.close)


    def showProductList(self, products):
        if self.productsContainer:
            self.clearProductList()

        self.productsContainer = QWidget(self.scrollAreaWidget)
        self.scrollAreaLayout.addWidget(self.productsContainer)

        self.productsLayout = QVBoxLayout(self.productsContainer)

        for pdt_info in products:
            item = ProductWidget(pdt_info, self.productsContainer)
            self.productsLayout.addWidget(item)
        self.productsLayout.addStretch()

        self.statusbar.showMessage("Showing %d items"%len(products))

    def clearProductList(self):
        if not self.productsContainer:
            return
        count = self.productsLayout.count() - 1 # last one is spacer item
        for i in reversed(range(count)):
            item = self.productsLayout.takeAt(i).widget()
            item.deleteLater()
        # remove last spacer item
        self.productsLayout.takeAt(0)

        self.scrollAreaLayout.removeWidget(self.productsContainer)
        self.productsContainer.deleteLater()


    def addNewProduct(self):
        dlg = ProductEditDialog(self)
        if dlg.exec()!=QDialog.Accepted:
            return
        name, brand, category, price, description, image = dlg.getValues()
        pdt_info = save_new_product(name, brand, category, price, description, image)
        widget = ProductWidget(pdt_info, self.productsContainer)
        self.productsLayout.insertWidget(self.productsLayout.count()-1, widget)
        return pdt_info

    def addNewPurchase(self):
        dlg = NewPurchaseDialog(self)
        if dlg.exec()==QDialog.Accepted:
            save_new_purchases(dlg.purchases)

    def showPurchaseHistory(self):
        dlg = PurchaseHistoryDialog(self)
        dlg.exec()

    def search(self, text=""):
        # filter products
        if text:
            result = []# list of (pdt_id, matches_count) tuple
            words = [x.lower() for x in text.split()]
            i = 0
            for product in App.products:
                product_name = product[1].lower()
                matches = 0 # number of matched words
                for word in words:
                    if word in product_name:
                        matches += 1
                if matches:
                    result.append((i, matches))
                i += 1
            # sort the result, according to number of matched words
            result = sorted(result, key=lambda x: x[1])
            products = [App.products[i[0]] for i in result]
        else:
            products = App.products
        self.showProductList(products)

    def clearData(self):
        dlg = ClearDataDialog(self)
        if dlg.exec()!=QDialog.Accepted:
            return
        # clear products data
        if dlg.productsBtn.isChecked():
            clear_products_data()
            self.showProductList(App.products)
        # clear purchases data
        if dlg.purchasesBtn.isChecked():
            clear_purchases_data()

    def showAbout(self):
        lines = ("<h1>PriceMem</h1>",
            "A Simple product price manager for small business shop <br><br>",
            "Version : %s<br>" % __version__,
            "Qt : %s<br>" % qVersion(),
            "Copyright &copy; %s %s &lt;%s&gt;" % (COPYRIGHT_YEAR, AUTHOR_NAME, AUTHOR_EMAIL))
        QMessageBox.about(self, "About PriceMem", "".join(lines))

    def closeEvent(self, ev):
        """ Save all settings on window close """
        if not self.isMaximized():
            self.settings.setValue("WindowWidth", self.width())
            self.settings.setValue("WindowHeight", self.height())
        self.settings.setValue("WindowMaximized", self.isMaximized())
        self.settings.setValue("LastProdID", App.last_product_id)


class ProductWidget(QWidget):

    def __init__(self, product_info, parent):
        self.product_info = product_info
        QWidget.__init__(self, parent)
        self.setStyleSheet("ProductWidget{background-color: white;}")
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        # add widgets
        layout = QGridLayout(self)
        self.thumbnail = QLabel(self)
        self.thumbnail.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.brand = QLabel(self)
        self.brand.setStyleSheet("QLabel { color: #333333;}")
        self.title = QLabel(self)
        self.title.setStyleSheet("QLabel { color: #000099;}")
        self.price = QLabel(self)
        # buttons
        self.editBtn = QToolButton(self)
        self.editBtn.setIcon(QIcon(":/icons/edit.png"))
        self.deleteBtn = QToolButton(self)
        self.deleteBtn.setIcon(QIcon(":/icons/delete.png"))
        self.historyBtn = QToolButton(self)
        self.historyBtn.setIcon(QIcon(":/icons/order-history.png"))
        # add to layout
        layout.addWidget(self.thumbnail, 0,0,3,1)
        layout.addWidget(self.brand, 0,1,1,1)
        layout.addWidget(self.editBtn, 0,2,1,1)
        layout.addWidget(self.deleteBtn, 0,3,1,1)
        layout.addWidget(self.historyBtn, 0,4,1,1)
        layout.addWidget(self.title, 1,1,1,4)
        layout.addWidget(self.price, 2,1,1,4)
        # connect signals
        self.editBtn.clicked.connect(self.edit)
        self.deleteBtn.clicked.connect(self.delete)
        self.historyBtn.clicked.connect(self.showHistory)

        self.update()

    def update(self):
        pdt_id, name, brand, category, price, description = self.product_info
        self.title.setText(name)
        self.brand.setText(brand)
        self.price.setText("Rs. %s/-"%price)
        # set image
        img = QImage(App.IMAGES_DIR + "/%s.jpg"%pdt_id)
        img = img.isNull() and App.product_icon or img.scaled(64,64)
        self.thumbnail.setPixmap(QPixmap.fromImage(img))
        #self.setToolTip(description)

    def paintEvent(self, paint_ev):
        """ this function is needed, otherwise stylesheet is not applied properly """
        o = QStyleOption()
        o.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, o, p, self)

    def edit(self):
        pdt_id = self.product_info[0]
        dlg = ProductEditDialog(self)
        dlg.setWindowTitle("Edit Product Details")
        img = QImage(App.IMAGES_DIR + "/%s.jpg"%pdt_id)
        if img.isNull():
            img = None
        dlg.setValues(*self.product_info[1:], img)
        if dlg.exec()!=QDialog.Accepted:
            return
        name, brand, category, price, description, image = dlg.getValues()
        self.product_info.clear()
        self.product_info += [pdt_id, name, brand, category, price, description]
        # save the product image
        if dlg.image_changed:
            img_filename = App.IMAGES_DIR + "/%s.jpg"%pdt_id
            if dlg.image and not image.isNull():
                if not os.path.exists(App.IMAGES_DIR):
                    os.mkdir(App.IMAGES_DIR)
                image.save(img_filename)
            else:
                # image changed and is None, means image has been removed
                if os.path.isfile(img_filename):# also checks if file exists
                    os.remove(img_filename)
        self.update()
        save_products_file()

    def delete(self):
        btn = QMessageBox.warning(self, "Delete Product ?",
                "Are you sure to delete the product permanently ?", QMessageBox.Ok|QMessageBox.Cancel)
        if btn!=QMessageBox.Ok:
            return
        img_filename = App.IMAGES_DIR + "/%s.jpg"%self.product_info[0]
        if os.path.exists(img_filename):
            os.remove(img_filename)
        App.products.remove(self.product_info)
        save_products_file()
        self.parent().layout().removeWidget(self)
        self.deleteLater()

    def showHistory(self):
        dlg = ProductHistoryDialog(self.product_info, self)
        dlg.exec()


class SearchBar(QLineEdit):
    # signals
    searchRequested = pyqtSignal(str)# str may be empty text

    def __init__(self, parent):
        QLineEdit.__init__(self, parent)
        self.setStyleSheet("QLineEdit { padding: 2 22 2 2; background: transparent; border: 1px solid gray; border-radius: 3px;}")
        # Create button for showing page icon
        self.searchButton = QToolButton(self)
        self.searchButton.setStyleSheet("QToolButton { border: 0; background: transparent; width: 16px; height: 16px; }")
        self.searchButton.setIcon(QIcon(':/icons/search.png'))
        #self.searchButton.setCursor(Qt.PointingHandCursor)

    def keyPressEvent(self, ev):
        # pressing escape clears text and emit searchRequest(empty_text) signal
        if ev.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Escape):
            if ev.key()==Qt.Key_Escape:
                self.clear()
            self.searchRequested.emit(self.text())
        QLineEdit.keyPressEvent(self, ev)

    def resizeEvent(self, ev):
        self.searchButton.move(self.width()-22,3)
        QLineEdit.resizeEvent(self, ev)


class ProductThumbnail(QLabel):
    # signals
    mousePressed = pyqtSignal(QPoint)

    def __init__(self, parent):
        QLabel.__init__(self, parent)

    def mousePressEvent(self, ev):
        self.mousePressed.emit(self.mapToGlobal(ev.pos()))

    def setImage(self, image):
        if image:
            self.setPixmap(QPixmap.fromImage(image.scaled(128,128,
                    Qt.KeepAspectRatio, Qt.SmoothTransformation)))
        else:
            self.setPixmap(QPixmap.fromImage(App.product_icon.scaled(128,128,Qt.KeepAspectRatio, Qt.SmoothTransformation)))


class ProductEditDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setWindowTitle("Add New Product")
        self.resize(380,200)

        self.imageLabel = ProductThumbnail(self)
        self.nameEdit = QLineEdit(self)
        self.nameEdit.setPlaceholderText("Name")
        self.brandEdit = QLineEdit(self)
        self.brandEdit.setPlaceholderText("Brand")
        self.categoryCombo = QComboBox(self)
        self.categoryCombo.addItems(["Unknown"] + categories)
        self.priceEdit = QLineEdit(self)
        self.priceEdit.setPlaceholderText("Price")
        self.descriptionEdit = QLineEdit(self)
        self.descriptionEdit.setPlaceholderText("Description")
        self.buttonbox = QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel, Qt.Horizontal, self)

        self.gridLayout = QGridLayout(self)
        self.gridLayout.addWidget(self.imageLabel, 0,0,3,1)
        self.gridLayout.addWidget(self.nameEdit, 0,1,1,2)
        self.gridLayout.addWidget(self.brandEdit, 1,1,1,2)
        self.gridLayout.addWidget(self.categoryCombo, 2,1,1,1)
        self.gridLayout.addWidget(self.priceEdit, 2,2,1,1)
        self.gridLayout.addWidget(self.descriptionEdit, 3,0,1,3)
        self.gridLayout.addWidget(self.buttonbox, 4,0,1,3)

        self.imageLabel.mousePressed.connect(self.showThumbnailMenu)
        self.buttonbox.accepted.connect(self.accept)
        self.buttonbox.rejected.connect(self.reject)

        self.image = None
        self.image_changed = False
        self.imageLabel.setImage(self.image)
        index = self.categoryCombo.findText(App.last_category)
        if index>=0:
            self.categoryCombo.setCurrentIndex(index)


    def setValues(self, name=None, brand=None, category=None, price=None, description=None, image=None):
        """ this function is used when new product is added """
        if name:
            self.nameEdit.setText(name)
        if brand:
            self.brandEdit.setText(brand)
        if category:
            index = self.categoryCombo.findText(category)
            if index>=0:
                self.categoryCombo.setCurrentIndex(index)
        if price:
            self.priceEdit.setText(price)
        if description:
            self.descriptionEdit.setText(description)
        if image:
            self.image = image
            self.imageLabel.setImage(self.image)

    def getValues(self):
        name = self.nameEdit.text()
        brand = self.brandEdit.text()
        category = self.categoryCombo.currentText()
        price = self.priceEdit.text()
        description = self.descriptionEdit.text()
        return name, brand, category, price, description, self.image


    def showThumbnailMenu(self, pos):
        menu = QMenu(self)
        menu.addAction("Change Photo", self.changeImage)
        if self.image:
            menu.addAction("Remove Photo", self.removeImage)
        menu.exec(pos)

    def changeImage(self):
        filename, filtr = QFileDialog.getOpenFileName(self, "Open File",
                        "", "All Images (*.jpg *.jpeg *.webp);;")
        if not filename:
            return
        image = QImage(filename)
        if not image.isNull():
            self.image = image.scaled(256,256, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            self.image_changed = True
            self.imageLabel.setImage(self.image)

    def removeImage(self):
        self.image = None
        self.image_changed = True
        self.imageLabel.setImage(self.image)


    def accept(self):
        if self.nameEdit.text()=="" or self.priceEdit.text()=="":
            return
        App.last_category = self.categoryCombo.currentText()
        QDialog.accept(self)



class ClearDataDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setWindowTitle("Clear Database")

        self.productsBtn = QCheckBox("Clear Products Data", self)
        self.purchasesBtn = QCheckBox("Clear Purchase Data", self)
        self.buttonbox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel, Qt.Horizontal, self)

        layout = QVBoxLayout(self)
        layout.addWidget(self.productsBtn)
        layout.addWidget(self.purchasesBtn)
        layout.addWidget(self.buttonbox)

        self.buttonbox.accepted.connect(self.accept)
        self.buttonbox.rejected.connect(self.reject)



def main():
    app = QApplication(sys.argv)
    #app.setOrganizationName("Arindamsoft")
    app.setApplicationName("PriceMem")
    # use fusion style on Windows platform
    #if platform.system()=="Windows" and "Fusion" in QStyleFactory.keys():
    #    app.setStyle(QStyleFactory.create("Fusion"))
    #global App.DATA_DIR, App.IMAGES_DIR
    App.DATA_DIR = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
    App.IMAGES_DIR = App.DATA_DIR + "/images"
    App.PRODUCTS_FILE = App.DATA_DIR + "/products.csv"
    App.PURCHASES_FILE = App.DATA_DIR + "/purchases.csv"
    # load window
    App.window = Window()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
