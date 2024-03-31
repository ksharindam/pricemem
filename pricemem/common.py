# -*- coding: utf-8 -*-
# This file is a part of PriceMem Program which is GNU GPLv3 licensed
# Copyright (C) 2024 Arindam Chaudhuri <arindamsoft94@gmail.com>
from PyQt5.QtCore import QStandardPaths
#import platform

# container for global variables
class App:
    # Various Data paths (overridden on app start)
    DATA_DIR =       "~/.local/share/PriceMem"
    IMAGES_DIR =     "~/.local/share/PriceMem/images"
    PRODUCTS_FILE =  "~/.local/share/PriceMem/products.csv"
    PURCHASES_FILE = "~/.local/share/PriceMem/purchases.csv"
    # each item is [pdt_id, name, brand, category, price, description]
    products = []
    # each item is [date, pdt_id, title, quantity, price]
    purchases = []
    last_product_id = "P00000"
    # the main window
    window = None
    # 64x64 QImage
    product_icon = None
    # product category of last added new product
    last_category = "Unknown"


# this function must be called after calling QApplication.setApplicationName()
def updateDataPaths():
    #if platform.system()=="Windows":
    App.DATA_DIR = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
    App.IMAGES_DIR = App.DATA_DIR + "/images"
    App.PRODUCTS_FILE = App.DATA_DIR + "/products.csv"
    App.PURCHASES_FILE = App.DATA_DIR + "/purchases.csv"
