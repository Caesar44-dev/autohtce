import os
import logging
import random
import urllib.request
import zipfile
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from tkinter import filedialog, Tk
from selenium import webdriver
import time
from PIL import Image
from reportlab.pdfgen import canvas
from io import BytesIO
from rembg import remove
import requests
import base64


def get_configs(filename="configs.txt", separator="="):
    config = {}
    try:
        with open(filename, "r") as file:
            for line in file:
                if not line.startswith("#"):
                    if separator in line:
                        name, value = line.strip().split(separator, 1)
                        config[name.strip()] = value.strip()

    except FileNotFoundError:
        print(f" - Error: No se encontró el archivo de configuración: {filename}")
        logging.error(f"Error: No se encontró el archivo de configuración: {filename}")
    except Exception as e:
        print(f" - Error al leer la configuración: {e}")
        logging.error(f"Error al leer la configuración: {e}")

    return config


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


def setup(
    width,
    height,
    base_temp_dir,
    chromedriver_url,
    zip_filename,
    extract_dir_name,
    sub_dir_name,
    executable_name,
):
    temp_dir = base_temp_dir
    zip_file_path = os.path.join(temp_dir, zip_filename)
    extract_dir = os.path.join(temp_dir, extract_dir_name)
    chromedriver_dir = os.path.join(extract_dir, sub_dir_name)
    chromedriver_path = os.path.join(chromedriver_dir, executable_name)

    os.makedirs(temp_dir, exist_ok=True)

    if not os.path.exists(chromedriver_path):
        logging.info("Descargando ChromeDriver...")
        urllib.request.urlretrieve(chromedriver_url, zip_file_path)

        logging.info("Descomprimiendo ChromeDriver...")
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        if not os.path.exists(chromedriver_path):
            error_message = f"El archivo {chromedriver_path} no se encontró después de la extracción."
            logging.error(error_message)
            raise FileNotFoundError(error_message)

        os.remove(zip_file_path)
    else:
        logging.info("ChromeDriver ya esta descargado.")

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument(f"--window-size={width},{height}")

    logging.info("Configurando el servicio de ChromeDriver...")

    try:
        service = ChromeService(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        time.sleep(2)
        logging.info("Inicializacion exitosa.")
        return driver, service
    except Exception as e:
        logging.error(f"Error durante la configuración: {e}")
        raise


# def initialize(driver):
#     try:
#         logging.info("Selecionando archivo html.")
#         print(" - Porfavor selecione el archivo html a capturar.")
#         html_file_path = select_html_file()
#         logging.info("Selecionando archivo html.")
#         driver.get(html_file_path)
#         time.sleep(2)
#         return html_file_path
#     except Exception as e:
#         logging.error(f"Error durante la Inicializacion: {e}")
#         # finalize(driver, service)
#         raise


def initialize(driver):
    try:
        logging.info("Seleccionando la carpeta principal.")
        print(" - Por favor, selecciona la carpeta principal.")

        main_folder_path = select_folder()

        html_files = []

        for subdir in next(os.walk(main_folder_path))[1]:
            subdir_path = os.path.join(main_folder_path, subdir)

            files_in_subdir = [
                os.path.join(subdir_path, f)
                for f in os.listdir(subdir_path)
                if f.endswith(".html") and os.path.isfile(os.path.join(subdir_path, f))
            ]

            html_files.extend(files_in_subdir)

        if not html_files:
            print(" - No se encontraron archivos HTML en la carpeta seleccionada.")
            return []

        logging.info(f"Archivos HTML encontrados: {html_files}")
        print(f" - Archivos HTML encontrados: {html_files}")

        return html_files

    except Exception as e:
        logging.error(f"Error durante la inicialización: {e}")
        raise


# def process(driver, html_file_path, width, height, quality, remove_text):
#     try:
#         logging.info("Iniciando la captura autamatica.")
#         print(" - Iniciando la captura autamatica.")

#         driver.switch_to.window(driver.window_handles[0])
#         time.sleep(2)

#         nav_folder_text = "Wiring Diagrams-All"
#         nav_table_iid = "files"
#         nav_page_a_css = "span.clsFig a.clsExtGraphicLink"
#         nav_folder_text2 = "Images"

#         file_name = os.path.splitext(os.path.basename(html_file_path))[0]
#         html_file_directory = os.path.dirname(html_file_path)

#         take_screenshot(driver, "home.png", (width, height))
#         compress_image("home.png", "compressed_home.jpeg", quality)

#         time.sleep(random.randint(1, 2))

#         nav_folder(driver, nav_folder_text)

#         nav_table(driver, nav_table_iid)

#         nav_page_a(driver, nav_page_a_css)

#         take_screenshot(driver, "page1.png", (width, height))
#         compress_image("page1.png", "compressed_page1.jpeg", quality)

#         driver.back()
#         time.sleep(random.randint(1, 2))
#         driver.back()

#         nav_folder(driver, nav_folder_text2)

#         nav_table_02(driver, nav_table_iid)

#         take_screenshot(driver, "page2.png", (width, height))
#         compress_image("page2.png", "compressed_page2.jpeg", quality)

#         time.sleep(random.randint(1, 2))

#         create_pdf(
#             ["compressed_home.jpeg", "compressed_page1.jpeg", "compressed_page2.jpeg"],
#             file_name,
#             html_file_directory,
#             width=width,
#             height=height,
#         )

#         remove_files(
#             [
#                 "home.png",
#                 "page1.png",
#                 "page2.png",
#                 "compressed_home.jpeg",
#                 "compressed_page1.jpeg",
#                 "compressed_page2.jpeg",
#             ]
#         )

#         time.sleep(random.randint(1, 2))

#         new_file_name = "Home.html"

#         dir_name = os.path.dirname(html_file_path)
#         output_zip_path = os.path.join(dir_name, file_name + ".zip")

#         compress_file_and_folder(html_file_path, new_file_name, output_zip_path)

#         time.sleep(random.randint(1, 2))

#         download_image_and_remove_background(
#             file_name, html_file_directory, remove_text, driver
#         )

#     except Exception as e:
#         logging.error(f"Error durante el procesamiento: {e}")
#         # finalize(driver, service)
#         raise


def process(
    driver,
    html_files,
    width,
    height,
    quality,
    remove_text,
    color_options_1,
    color_options_2,
):
    try:
        logging.info("Iniciando la captura automática.")
        print(" - Iniciando la captura automática.")

        for html_file_path in html_files:
            logging.info(f"Procesando archivo HTML: {html_file_path}")
            print(f" - Procesando archivo HTML: {html_file_path}")

            driver.get(f"file://{html_file_path}")
            time.sleep(2)

            file_name = os.path.splitext(os.path.basename(html_file_path))[0]
            html_file_directory = os.path.dirname(html_file_path)

            take_screenshot(driver, "home.png", (width, height))
            compress_image("home.png", "compressed_home.jpeg", quality)

            time.sleep(random.randint(1, 2))

            nav_folder(driver, "Wiring Diagrams-All")
            nav_table(driver, "files")
            nav_page_a(driver, "span.clsFig a.clsExtGraphicLink")

            take_screenshot(driver, "page1.png", (width, height))
            compress_image("page1.png", "compressed_page1.jpeg", quality)

            driver.back()
            time.sleep(random.randint(1, 2))
            driver.back()

            nav_folder(driver, "Images")
            nav_table_02(driver, "files")

            take_screenshot(driver, "page2.png", (width, height))
            compress_image("page2.png", "compressed_page2.jpeg", quality)

            time.sleep(random.randint(1, 2))

            create_pdf(
                [
                    "compressed_home.jpeg",
                    "compressed_page1.jpeg",
                    "compressed_page2.jpeg",
                ],
                file_name,
                html_file_directory,
                width=width,
                height=height,
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

            time.sleep(random.randint(1, 2))

            new_file_name = "Home.html"
            output_zip_path = os.path.join(html_file_directory, file_name + ".zip")

            compress_file_and_folder(html_file_path, new_file_name, output_zip_path)

            time.sleep(random.randint(1, 2))

            download_image_and_remove_background(
                file_name,
                html_file_directory,
                remove_text,
                driver,
                color_options_1,
                color_options_2,
            )

    except Exception as e:
        logging.error(f"Error durante el procesamiento: {e}")
        raise


def finalize(driver, service):
    logging.info("Cerrando el navegador y deteniendo el servicio.")
    print(" - Cerrando el navegador y deteniendo el servicio.")
    driver.quit()
    service.stop()


def restart():
    while True:
        response = input(" - ¿Volver a iniciar? (si/no): ").lower()
        if response in ["si", "s"]:
            return True
        elif response in ["no", "n"]:
            return False
        else:
            print(" - Por favor, introduce 'si', 'no', 's' o 'n'.")


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
        logging.info(f"Navegando en: {idd}")
        xpath = f"//table[@id='{idd}']//tbody/tr[1]//a"
        link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        link.click()
    except Exception as e:
        logging.error(f"Error al hacer clic en el primer enlace de la tabla: {e}")
        finalize(driver, service)
        raise


def nav_table_02(driver, idd):
    try:
        logging.info(f"Navegando en: {idd}")

        rows_xpath = f"//table[@id='{idd}']//tbody/tr"
        rows = driver.find_elements(By.XPATH, rows_xpath)
        num_rows = len(rows)

        if num_rows == 0:
            logging.warning("No se encontraron filas en la tabla.")
            return

        random_row = random.randint(1, num_rows)

        xpath = f"//table[@id='{idd}']//tbody/tr[{random_row}]//a"
        link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        link.click()
    except Exception as e:
        logging.error(f"Error al hacer clic en el primer enlace de la tabla: {e}")
        finalize(driver, service)
        raise


def nav_page_a(driver, selector_css):
    logging.info(f"Navegando en: {selector_css}")
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


def take_screenshot(driver, file_name, window_size):
    try:
        driver.set_window_size(*window_size)
        driver.save_screenshot(file_name)
        logging.info(f"Captura de pantalla guardada como: {file_name}")
    except Exception as e:
        logging.error(f"Error al tomar la captura de pantalla: {e}")
        finalize(driver, service)
        raise


# def select_html_file():
#     try:
#         root = Tk()
#         root.withdraw()
#         file_path = filedialog.askopenfilename(filetypes=[("Archivos HTML", "*.html")])
#         if not file_path:
#             print(" - Selección de archivo cancelada.")
#             logging.warning("Selección de archivo cancelada.")
#         else:
#             print(f" - Archivo seleccionado: {file_path}")
#         return file_path
#     except Exception as e:
#         print(f" - Error al seleccionar el archivo HTML: {e}")
#         logging.error(f"Error al seleccionar el archivo HTML: {e}")
#         raise


def select_folder():
    try:
        root = Tk()
        root.withdraw()
        folder_path = filedialog.askdirectory()
        if not folder_path:
            print(" - Selección de carpeta cancelada.")
            logging.warning("Selección de carpeta cancelada.")
        else:
            print(f" - Carpeta seleccionada: {folder_path}")
        return folder_path
    except Exception as e:
        print(f" - Error al seleccionar la carpeta: {e}")
        logging.error(f"Error al seleccionar la carpeta: {e}")
        raise


def compress_image(image_path, output_path, quality):
    try:
        image = Image.open(image_path)
        if image.mode == "RGBA":
            image = image.convert("RGB")
        image.save(output_path, "JPEG", quality=quality, optimize=True)
    except Exception as e:
        logging.error(f"Error al comprimir la imagen: {e}")
        finalize(driver, service)
        raise


def create_pdf(images, file_name, html_file_directory, width, height):
    try:
        packet = BytesIO()
        pdf = canvas.Canvas(packet, pagesize=(width, height))

        for image_path in images:
            pdf.drawImage(image_path, 0, 0, width=width, height=height)
            pdf.showPage()

        pdf.save()

        packet.seek(0)
        pdf_path = os.path.join(html_file_directory, f"Vista Previa {file_name}.pdf")

        with open(pdf_path, "wb") as output_file:
            output_file.write(packet.read())

        print(f" - Captura completada: {pdf_path}")
        logging.info(f"PDF creado: {pdf_path}")

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


def compress_file_and_folder(html_file_path, new_file_name, output_zip_path):
    try:
        print(f" - Verificando existencia del archivo: {html_file_path}")
        if not os.path.exists(html_file_path):
            raise FileNotFoundError(f"El archivo '{html_file_path}' no existe.")

        dir_name = os.path.dirname(html_file_path)
        base_name = os.path.splitext(os.path.basename(html_file_path))[0]
        folder_path = os.path.join(dir_name, base_name)

        new_file_path = os.path.join(dir_name, new_file_name)
        os.rename(html_file_path, new_file_path)

        with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(new_file_path, new_file_name)

            for foldername, subfolders, filenames in os.walk(folder_path):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    arcname = os.path.join(
                        os.path.basename(folder_path),
                        os.path.relpath(file_path, folder_path),
                    )
                    zipf.write(file_path, arcname)

                for subfolder in subfolders:
                    folder_path_inside_zip = os.path.join(
                        os.path.basename(folder_path),
                        os.path.relpath(
                            os.path.join(foldername, subfolder), folder_path
                        ),
                    )
                    zipf.write(
                        os.path.join(foldername, subfolder), folder_path_inside_zip
                    )

        print(
            f" - Archivo {html_file_path} renombrado a {new_file_name} y comprimido en {output_zip_path} junto con la carpeta {folder_path}"
        )

    except FileNotFoundError as e:
        print(f" - Error: {e}")
        logging.error(f"Error durante el procesamiento: {e}")
        raise
    except PermissionError as e:
        print(f" - Error de permisos: {e}")
        logging.error(f"Error de permisos: {e}")
        raise
    except Exception as e:
        print(f" - Error general: {e}")
        logging.error(f"Error general: {e}")
        raise


def download_image_and_remove_background(
    file_name, save_directory, remove_text, driver, color_options_1, color_options_2
):
    try:
        url = "https://www.google.com/imghp"
        driver.get(url)

        search_box = driver.find_element(By.NAME, "q")
        time.sleep(random.uniform(1, 2))

        file_name_lower = file_name.lower()
        remove_text_lower = remove_text.lower()
        search_text = file_name_lower.replace(remove_text_lower, "")

        search_box.send_keys(search_text + Keys.RETURN)
        logging.info("Busqueda completada.")
        print(" - Busqueda completada.")

        time.sleep(random.uniform(2, 3))

        select_color(driver, color_options_1, color_options_2)

        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div.GyAeWb.gIatYd img")
            )
        )

        all_images = driver.find_elements(By.CSS_SELECTOR, "div.GyAeWb.gIatYd img")
        images = [
            img
            for img in all_images
            if "YQ4gaf" in img.get_attribute("class")
            and len(img.get_attribute("class").split()) == 1
        ]

        if images:
            image_number = int(
                input("Ingrese el número de la imagen a descargar (0, 1, 2, etc..): ")
            )
            if 0 <= image_number < len(images):
                image_element = images[image_number]
            else:
                print(
                    f" - El número de imagen {image_number} esta fuera de rango. Solo hay {len(images)} imágenes disponibles."
                )
                return
        else:
            print(
                " - No se encontraron imágenes con solo la clase 'YQ4gaf' dentro del div especificado."
            )
            return

        time.sleep(2)

        image_url = image_element.get_attribute("src")

        if image_url.startswith("data:image"):
            header, encoded = image_url.split(",", 1)
            data = base64.b64decode(encoded)
            img = Image.open(BytesIO(data))
        else:
            response = requests.get(image_url)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))

        os.makedirs(save_directory, exist_ok=True)

        # original_image_path = os.path.join(save_directory, "original_image.png")
        # img.save(original_image_path)

        img_no_bg = remove(img)

        no_bg_image_path = os.path.join(save_directory, file_name + ".png")
        img_no_bg.save(no_bg_image_path)

        print(f" - Imagen guardada en {no_bg_image_path}")

    except Exception as e:
        logging.error(f"Error general: {str(e)}")
        print(f" - Error general: {str(e)}")
        finalize(driver, service)
        raise


# def select_color(option, driver):
#     try:
#         logging.info("Iniciando selección de color...")

#         tools = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.ID, "hdtb-tls"))
#         )
#         tools.click()

#         color_elements = WebDriverWait(driver, 10).until(
#             EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.KTBKoe"))
#         )
#         color_elements[1].click()

#         logging.info(" - Menú de herramientas desplegado.")
#         print(" - Menú de herramientas desplegado.")

#         menu = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "g-menu[jsname='xl07Ob']")))
#         menu.click()

#         options = driver.find_elements(By.CSS_SELECTOR, 'div.YpcDnf.OSrXXb.HG1dvd a')

#         options[option].click()

#     except Exception as e:
#         logging.error(f"Error general: {str(e)}")
#         print(f" - Error general: {str(e)}")
#         finalize(driver, service)
#         raise


def select_color(driver, color_options_1, color_options_2):
    try:

        while True:
            try:
                color_number = int(
                    input(
                        f"Ingrese el numero del color (0 - {color_options_1}, 1 - {color_options_2}): "
                    )
                )
                if color_number in [0, 1]:
                    break
                else:
                    print("Por favor, ingrese un número válido (0 o 1).")
            except ValueError:
                print("Entrada no válida. Por favor, ingrese un número.")

        logging.info("Iniciando selección de color...")

        # Espera hasta que el menú de herramientas esté disponible y haz clic
        tools = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "hdtb-tls"))
        )
        tools.click()
        logging.info(" - Menú de herramientas desplegado.")
        print(" - Menú de herramientas desplegado.")

        # Espera hasta que los elementos de color estén disponibles y selecciona el segundo elemento
        color_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.KTBKoe"))
        )
        color_elements[1].click()

        # Define las opciones de color
        color_options = {
            0: f'//g-menu-item[@jsname="NNJLud"]//a[text()="{color_options_1}"]',
            1: f'//g-menu-item[@jsname="NNJLud"]//a[text()="{color_options_2}"]',
        }

        # Selección del color basado en la entrada del usuario
        if color_number in color_options:
            try:
                menu_item = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, color_options[color_number]))
                )
                menu_item.click()
                logging.info(f" - Color seleccionado: {color_options[color_number]}.")
                print(
                    f" - Color seleccionado exitosamente: {color_options[color_number]}."
                )
            except Exception as e:
                logging.error(f" - Error al seleccionar el color: {e}")
                print(" - Error al seleccionar el color.")
        else:
            logging.error(" - Opción de color no válida.")
            print(" - Opción de color no válida.")

    except Exception as e:
        logging.error(f"Error general: {str(e)}")
        print(f" - Error general: {str(e)}")
        finalize(driver, service)
        raise


if __name__ == "__main__":
    configs = get_configs()
    width = int(configs.get("width"))
    height = int(configs.get("height"))
    quality = int(configs.get("quality"))
    extensions_path = str(configs.get("extensions_path"))

    base_temp_dir = str(configs.get("base_temp_dir"))
    chromedrive_url = str(configs.get("chromedrive_url"))
    zip_path = str(configs.get("zip_path"))
    extract_dir = str(configs.get("extract_dir"))
    sub_dir_name = str(configs.get("sub_dir_name"))
    executable_name = str(configs.get("executable_name"))

    remove_text = str(configs.get("remove_text"))

    color_options_1 = str(configs.get("color_options_1"))
    color_options_2 = str(configs.get("color_options_2"))

    configure_logging()

    while True:
        try:
            driver, service = setup(
                width,
                height,
                base_temp_dir,
                chromedrive_url,
                zip_path,
                extract_dir,
                sub_dir_name,
                executable_name,
            )
            html_file_path = initialize(driver)
            process(driver, html_file_path, width, height, quality, remove_text, color_options_1, color_options_2)
        except Exception as e:
            logging.error(f"Error general: {e}")
            finalize(driver, service)
        # finally:
        #     finalize(driver, service)

        if not restart():
            finalize(driver, service)
            break
