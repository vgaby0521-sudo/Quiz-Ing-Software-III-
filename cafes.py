import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


ruta_escritorio = os.path.join(os.path.expanduser("~"), "Desktop")

opciones = Options()
opciones.add_argument("--start-maximized")

navegador = webdriver.Chrome(options=opciones)
url = "https://coffee-cart.app"
navegador.get(url)


def tomar_captura(nombre):
    archivo = os.path.join(ruta_escritorio, f"{nombre}.png")
    navegador.save_screenshot(archivo)
    print(f"Captura guardada: {archivo}")

def escribir_campo(by, selector, texto, timeout=10):
    campo = WebDriverWait(navegador, timeout).until(
        EC.element_to_be_clickable((by, selector))
    )
    campo.clear()
    campo.send_keys(texto)
    return campo

def clic_elemento(by, selector, timeout=10):
    elemento = WebDriverWait(navegador, timeout).until(
        EC.element_to_be_clickable((by, selector))
    )
    elemento.click()
    return elemento

def asegurar_modal_abierto():
    try:
        modal = WebDriverWait(navegador, 2).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "modal-content"))
        )
        return modal
    except:
        WebDriverWait(navegador, 10).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "snackbar"))
        )
        clic_elemento(By.CSS_SELECTOR, '[data-test="checkout"]')
        return WebDriverWait(navegador, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "modal-content"))
        )

# Enlaces, Menu
assert "Coffee cart" in navegador.title
enlace_menu = navegador.find_element(By.LINK_TEXT, "menu")
enlace_carrito = navegador.find_element(By.PARTIAL_LINK_TEXT, "cart")
enlace_github = navegador.find_element(By.LINK_TEXT, "github")
assert enlace_menu.is_displayed()
assert enlace_carrito.is_displayed()
assert enlace_github.is_displayed()
tomar_captura("menu")

# Carrito vacío
assert "cart (0)" in enlace_carrito.text
tomar_captura("carrito_vacio")

# Agregar café y validar carrito
def agregar_cafe(nombre_cafe, cantidad_esperada, nombre_captura):
    clic_elemento(By.CSS_SELECTOR, f'[data-test="{nombre_cafe}"]')
    carrito = navegador.find_element(By.PARTIAL_LINK_TEXT, "cart")
    assert f"cart ({cantidad_esperada})" in carrito.text
    tomar_captura(nombre_captura)

# agregar cafés 
agregar_cafe("Mocha", 1, "gregar_mocha")
agregar_cafe("Americano", 2, "agregar_americano")
agregar_cafe("Cappuccino", 3, "agregar_cappuccino")
agregar_cafe("Mocha", 4, "agregar_mocha_dos")
agregar_cafe("Mocha", 5, "agregar_mocha_tres")

# carrito con productos 
enlace_carrito = navegador.find_element(By.PARTIAL_LINK_TEXT, "cart")
assert "cart (0)" not in enlace_carrito.text
tomar_captura("carrito_con_productos")

# abrir modal de pago
clic_elemento(By.CSS_SELECTOR, '[data-test="checkout"]')
modal = WebDriverWait(navegador, 10).until(
    EC.visibility_of_element_located((By.CLASS_NAME, "modal-content"))
)
assert modal.is_displayed()
tomar_captura("modal_pago")

# formulario de pago
campo_nombre = escribir_campo(By.ID, "name", "")
campo_email = escribir_campo(By.ID, "email", "")
boton_enviar = WebDriverWait(navegador, 10).until(
    EC.element_to_be_clickable((By.ID, "submit-payment"))
)

#  formulario vacío 
boton_enviar.click()
tomar_captura("formulario_vacio")

# solo nombre 
escribir_campo(By.ID, "name", "David")
clic_elemento(By.ID, "submit-payment")
tomar_captura("solo_nombre")

# solo email ---
escribir_campo(By.ID, "name", "")  # Limpiamos nombre
escribir_campo(By.ID, "email", "david@gmail.com")
clic_elemento(By.ID, "submit-payment")
tomar_captura("solo_email")

# datos incorrectos 
asegurar_modal_abierto()
escribir_campo(By.ID, "name", "12345")
escribir_campo(By.ID, "email", "correo_invalido")
clic_elemento(By.ID, "submit-payment")
tomar_captura("datos_incorrectos")

# formulario correcto y checkbox
asegurar_modal_abierto()
escribir_campo(By.ID, "name", "David")
escribir_campo(By.ID, "email", "david@gmail.com")

checkbox_promo = clic_elemento(By.ID, "promotion")
assert checkbox_promo.is_selected()
tomar_captura("checkbox_promo")

clic_elemento(By.ID, "submit-payment")
tomar_captura("formulario_correcto")


# eliminar un producto del carrito 
agregar_cafe("Mocha", 1, "eliminar")

clic_elemento(By.PARTIAL_LINK_TEXT, "cart")

boton_menos = WebDriverWait(navegador, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label^="Remove one"]'))
)
navegador.execute_script("arguments[0].click();", boton_menos)

tomar_captura("producto_eliminado")


# refrescar página y validar persistencia del carrito 
navegador.refresh()
enlace_carrito = navegador.find_element(By.PARTIAL_LINK_TEXT, "cart")
tomar_captura("refresh")


navegador.quit()
print("Pruebas completadas")
