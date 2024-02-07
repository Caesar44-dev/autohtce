import os
import logging
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from tkinter import filedialog, Tk
from selenium import webdriver
import time
from PIL import Image
from reportlab.pdfgen import canvas
from io import BytesIO


def configure_logging():
    try:
        logging.basicConfig(
            filename="app.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
    except Exception as e:
        logging.error(f"Error al configurar el registro: {e}")
        raise


def setup():
    try:
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--log-level=3")
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        time.sleep(2)
        return driver, service
    except Exception as e:
        logging.error(f"Error durante la configuración: {e}")
        finalize(driver, service)
        raise


def initialize(driver):
    try:
        html_file_path = select_html_file()
        driver.get(html_file_path)
        time.sleep(2)
        logging.info("Inicialización exitosa.")
        return html_file_path
    except Exception as e:
        logging.error(f"Error durante la inicialización: {e}")
        finalize(driver, service)
        raise


def process(driver, html_file_path):
    try:
        nav_folder_text = "Wiring Diagrams-All"
        nav_table_iid = "files"
        nav_page_a_css = "span.clsFig a.clsExtGraphicLink"
        nav_folder_text2 = "Images"

        file_name = os.path.splitext(os.path.basename(html_file_path))[0]
        time.sleep(random.randint(1, 2))

        take_screenshot(driver, "home.png")
        compress_image("home.png", "compressed_home.jpeg")

        time.sleep(random.randint(1, 2))

        nav_folder(driver, nav_folder_text)
        time.sleep(random.randint(1, 2))

        nav_table(driver, nav_table_iid)
        time.sleep(random.randint(1, 2))

        nav_page_a(driver, nav_page_a_css)
        time.sleep(random.randint(1, 2))

        take_screenshot(driver, "page1.png")
        compress_image("page1.png", "compressed_page1.jpeg")
        time.sleep(random.randint(1, 2))

        driver.back()
        time.sleep(random.randint(1, 2))
        driver.back()
        time.sleep(random.randint(1, 2))

        nav_folder(driver, nav_folder_text2)
        time.sleep(random.randint(1, 2))

        nav_table(driver, nav_table_iid)
        time.sleep(random.randint(1, 2))

        take_screenshot(driver, "page2.png")
        compress_image("page2.png", "compressed_page2.jpeg")
        time.sleep(random.randint(1, 2))

        create_pdf(
            ["compressed_home.jpeg", "compressed_page1.jpeg", "compressed_page2.jpeg"],
            file_name,
            width=1200,
            height=800,
        )

        remove_files(
            [
                "home.png",
                "page1.png",
                "page2.png",
                "compressed_home.jpeg",
                "compressed_page1.jpeg",
                "compressed_page2.jpeg",
            ]
        )

    except Exception as e:
        logging.error(f"Error durante el procesamiento: {e}")
        finalize(driver, service)
        raise


def finalize(driver, service):
    logging.info("Cerrando el navegador y deteniendo el servicio.")
    driver.quit()
    service.stop()


def nav_folder(driver, text):
    try:
        logging.info(f"Navegando a la carpeta: {text}")
        xpath = f"//a[text()='{text}']"
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        element.click()
    except Exception as e:
        logging.error(f"Error al navegar a la carpeta: {e}")
        finalize(driver, service)
        raise


def nav_table(driver, idd):
    try:
        xpath = f"//table[@id='{idd}']//tbody/tr[1]//a"
        link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        link.click()
    except Exception as e:
        logging.error(f"Error al hacer clic en el primer enlace de la tabla: {e}")
        finalize(driver, service)
        raise


def nav_page_a(driver, selector_css):
    try:
        elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector_css))
        )
        if elements:
            elements[0].click()
        else:
            logging.error(
                "No se encontraron elementos con el selector CSS proporcionado."
            )
            finalize(driver, service)
            raise
    except Exception as e:
        logging.error(f"Error al navegar a la página: {e}")
        finalize(driver, service)
        raise


def take_screenshot(driver, file_name, window_size=(1200, 800)):
    try:
        driver.set_window_size(*window_size)
        driver.save_screenshot(file_name)
        logging.info(f"Captura de pantalla guardada como: {file_name}")
    except Exception as e:
        logging.error(f"Error al tomar la captura de pantalla: {e}")
        finalize(driver, service)
        raise


def select_html_file():
    try:
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(filetypes=[("Archivos HTML", "*.html")])
        return file_path
    except Exception as e:
        logging.error(f"Error al seleccionar el archivo HTML: {e}")
        finalize(driver, service)
        raise


def nav_table(driver, idd):
    xpath = f"//table[@id='{idd}']//tbody/tr[1]//a"
    try:
        link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        link.click()
    except Exception as e:
        logging.error(f"Error al hacer clic en el primer enlace de la tabla: {e}")
        finalize(driver, service)
        raise


def nav_page_a(driver, selector_css):
    elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector_css))
    )
    if elements:
        elements[0].click()
    else:
        logging.error("No se encontraron elementos con el selector CSS proporcionado.")
        finalize(driver, service)
        raise


def compress_image(image_path, output_path, quality=85):
    try:
        image = Image.open(image_path)
        if image.mode == "RGBA":
            image = image.convert("RGB")
        image.save(output_path, "JPEG", quality=quality, optimize=True)
    except Exception as e:
        logging.error(f"Error al comprimir la imagen: {e}")
        finalize(driver, service)
        raise


def create_pdf(images, file_name, width, height):
    try:
        packet = BytesIO()
        pdf = canvas.Canvas(packet, pagesize=(width, height))

        for image_path in images:
            pdf.drawImage(image_path, 0, 0, width=width, height=height)
            pdf.showPage()

        pdf.save()

        packet.seek(0)
        final_pdf_path = f"{file_name}.pdf"
        with open(final_pdf_path, "wb") as output_file:
            output_file.write(packet.read())

        logging.info(f"PDF creado: {final_pdf_path}")

    except Exception as e:
        logging.error(f"Error al crear el PDF: {e}")
        finalize(driver, service)
        raise


def remove_files(file_list):
    for file_path in file_list:
        try:
            os.remove(file_path)
        except Exception as e:
            logging.error(f"Error al eliminar el archivo {file_path}: {e}")
            finalize(driver, service)
            raise


if __name__ == "__main__":
    configure_logging()
    try:
        driver, service = setup()
        html_file_path = initialize(driver)
        process(driver, html_file_path)
    except Exception as e:
        logging.error(f"Error general: {e}")
    finally:
        finalize(driver, service)
