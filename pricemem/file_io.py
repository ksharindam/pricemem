# -*- coding: utf-8 -*-
# This file is a part of PriceMem Program which is GNU GPLv3 licensed
# Copyright (C) 2024 Arindam Chaudhuri <arindamsoft94@gmail.com>
import os, shutil
import csv
from common import App

def csv_string(text):
    """ quotes string for csv when required """
    delimiters = (",", ";", "\t", '"')# double quote is not delimiter
    for d in delimiters:
        if d in text:
            # double quote inside string should be replaced with two double quotes
            return '"%s"' % text.replace('"', '""')
    return text


def read_products_file():
    """ read products file and return list of products """
    try:
        f = open(App.PRODUCTS_FILE)
        reader = csv.reader(f)
        products = [row for row in reader if len(row)==6]
        # ignore the header line
        return products[1:]
    except FileNotFoundError:
        return []


def save_products_file():
    """ save whole products data into products file """
    if not os.path.exists(App.DATA_DIR):
        os.makedirs(App.DATA_DIR)
    with open(App.PRODUCTS_FILE, "w") as f:
        # header line
        f.write("ID, Name, Brand, Category, Price, Description\n")
        for item in App.products:
            f.write("%s,%s,%s,%s,%s,%s\n" % tuple(map(csv_string, item)))

def save_new_product(name, brand, category, price, description, image):
    """ append new product data to products file, and save the product image """
    # generate new product id
    pdt_id = "P%05d" % (int(App.last_product_id[1:])+1)

    # this means existing products file is corrupted
    if not App.products and os.path.exists(App.PRODUCTS_FILE):
        clear_products_data()
    # create products data file if not exist, and create the first line
    if not os.path.exists(App.PRODUCTS_FILE):
        if not os.path.exists(App.PURCHASES_FILE):# none of the data files exist
            clear_products_data()# resets pdt_id and deletes images
        if not os.path.exists(App.DATA_DIR):
            os.makedirs(App.DATA_DIR)
        f = open(App.PRODUCTS_FILE, "w")
        f.write("ID, Name, Brand, Category, Price, Description\n")
        f.close()

    item = [pdt_id, name, brand, category, price, description]

    with open(App.PRODUCTS_FILE, "a") as f:
        f.write("%s,%s,%s,%s,%s,%s\n" % tuple(map(csv_string, item)))
    # save the product image
    if image and not image.isNull():
        if not os.path.exists(App.IMAGES_DIR):
            os.mkdir(App.IMAGES_DIR)
        image.save(App.IMAGES_DIR + "/%s.jpg"%pdt_id)

    App.products.append(item)
    App.last_product_id = pdt_id
    return item




def read_purchases_file():
    purchases = []
    try:
        f = open(App.PURCHASES_FILE)
        reader = csv.reader(f)
        purchases = [row for row in reader if len(row)==5]
        # ignore the header line
        return purchases[1:]
    except FileNotFoundError:
        return []

def save_purchases_file():
    # sort purchases according to date
    App.purchases.sort(key=lambda x : x[0])

    if not os.path.exists(App.DATA_DIR):
        os.makedirs(App.DATA_DIR)
    with open(App.PURCHASES_FILE, "w") as f:
        # header line
        f.write("Date, Product ID, Title, Quantity, Price\n")
        for item in App.purchases:
            f.write("%s,%s,%s,%s,%s\n" % tuple(map(csv_string, item)))


def save_new_purchases(purchases):
    # create purchases data file if not exist, and create the first header line
    if not os.path.exists(App.PURCHASES_FILE):
        if not os.path.exists(App.DATA_DIR):
            os.makedirs(App.DATA_DIR)
        f = open(App.PURCHASES_FILE, "w")
        f.write("Date, Product ID, Title, Quantity, Price\n")
        f.close()

    with open(App.PURCHASES_FILE, "a") as f:
        for item in purchases:
            f.write("%s,%s,%s,%s,%s\n" % tuple(map(csv_string, item)))

    App.purchases += purchases


def clear_products_data():
    # delete products file
    if os.path.exists(App.PRODUCTS_FILE):
        os.remove(App.PRODUCTS_FILE)
    # delete images
    if os.path.exists(App.IMAGES_DIR):
        shutil.rmtree(App.IMAGES_DIR)
    # reset last product id
    App.products.clear()
    App.last_product_id = "P00000"

def clear_purchases_data():
    # delete purchases file
    if os.path.exists(App.PURCHASES_FILE):
        os.remove(App.PURCHASES_FILE)
    App.purchases.clear()

