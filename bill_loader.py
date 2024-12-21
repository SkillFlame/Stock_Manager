from PIL import Image
import pytesseract
import re
import csv
from datetime import datetime, timezone
import logging
from logging.handlers import TimedRotatingFileHandler
import sys
import os


class Product:
    def __init__(self, doc_number, date, supplier, name, reference, quantity, pvp):
        self.doc_number = doc_number
        self.date = date
        self.supplier = supplier
        self.name = name
        self.reference = reference
        self.quantity = quantity
        self.pvp = pvp

class Loader:

    def __init__(self, entry_path, exit_path, log_path):
        self.source_path = entry_path
        self.replica_path = exit_path
        self.log_path = log_path
        
        self.log = self.get_logger()
        self.files_hash = {}
    

    def get_logger(self):
        """Initializes logger

        Returns:
            logger
        """
        formatter = logging.Formatter("%(asctime)s — %(levelname)s — %(message)s")
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        file_handler = TimedRotatingFileHandler(self.log_path + "/synch.log", when='midnight')
        file_handler.setFormatter(formatter)
        
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG) 
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        logger.propagate = False
        
        return logger

    def get_files(self, path):
        file_list = []
        for root, folders, files in os.walk(path):
            for file in files:
                file_list.append(os.path.join(root, file))
        return file_list
                

    def write_csv(self, products):
        filename = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S') + '.csv'
        # Open the file in write mode
        with open(filename, mode='w', newline='') as file:
            # Create a CSV writer object
            writer = csv.writer(file)
            
            # Write the header (column names)
            writer.writerow(['doc_number', 'date', 'supplier', 'name', 'reference', 'quantity', 'pvp'])
            
            # Write the data for each product
            for product in products:
                writer.writerow([product.doc_number, product.date, product.supplier, product.name, product.reference, product.quantity, product.pvp])


    def parse_doc(self, path):
        file = pytesseract.image_to_string(Image.open(path))

        doc_supplier = re.findall(r"Termos do Acordo.*NIF.*(\b\d+)", file)[0]
        doc_number = re.findall(r"Turno\n(\b\d+)", file)[0]
        doc_date = re.findall(r"Data: (\d{2}/\d{2}/\d{4})", file)[0]
        doc_products = re.findall(r"N..Pacotes.*\n(.*\n)", file)

        products = []
        for product in doc_products:
            product = product.strip("\n").split(" ")
            products.append(Product(doc_number, doc_date, doc_supplier, " ".join(product[:-6]), product[-6], product[-5] ,product[-4]))

        return products


if __name__ == "__main__":
    #write_csv(parse_doc("FACTURA SAMPLE.png"))
    print(Loader("./","./","./").get_files("/home/skillflame/Documents/Stock_Manager"))
