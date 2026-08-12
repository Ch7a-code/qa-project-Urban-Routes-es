import time

import data
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


# no modificar
def retrieve_phone_code(driver) -> str:
    """Este código devuelve un número de confirmación de teléfono y lo devuelve como un string.
    Utilízalo cuando la aplicación espere el código de confirmación para pasarlo a tus pruebas.
    El código de confirmación del teléfono solo se puede obtener después de haberlo solicitado en la aplicación."""

    import json
    import time
    from selenium.common import WebDriverException
    code = None
    for i in range(10):
        try:
            logs = [log["message"] for log in driver.get_log('performance') if log.get("message")
                    and 'api/v1/number?number' in log.get("message")]
            for log in reversed(logs):
                message_data = json.loads(log)["message"]
                body = driver.execute_cdp_cmd('Network.getResponseBody',
                                              {'requestId': message_data["params"]["requestId"]})
                code = ''.join([x for x in body['body'] if x.isdigit()])
        except WebDriverException:
            time.sleep(1)
            continue
        if not code:
            raise Exception("No se encontró el código de confirmación del teléfono.\n"
                            "Utiliza 'retrieve_phone_code' solo después de haber solicitado el código en tu aplicación.")
        return code


class UrbanRoutesPage:
    # Direcciones (ejemplo provisto)
    from_field = (By.ID, 'from')
    to_field = (By.ID, 'to')
    call_taxi_button = (By.XPATH, "//button[contains(text(), 'Call a taxi')]")

    # Tarifa Comfort
    comfort_tariff = (By.XPATH, "//div[@class='tcard-title' and text()='Comfort']")

    # Teléfono
    phone_button = (By.CLASS_NAME, 'np-button')
    phone_field = (By.ID, 'phone')
    next_button = (By.XPATH, "//div[contains(@class, 'number-picker')]//button[contains(text(), 'Next')]")
    code_field = (By.ID, 'code')
    confirm_phone_button = (By.XPATH, "//div[contains(@class, 'number-picker')]//button[contains(text(), 'Confirm')]")

    # Tarjeta de crédito
    payment_method_button = (By.CLASS_NAME, 'pp-button')
    add_card_button = (By.XPATH, "//div[contains(@class, 'pp-plus-container')]")
    card_number_field = (By.XPATH, "//div[contains(@class, 'card-number-input')]//input")
    card_code_field = (By.XPATH, "//div[contains(@class, 'card-code-input')]//input")
    add_card_link_button = (By.XPATH, "//div[contains(@class, 'pp-buttons')]//button[contains(text(), 'Add')]")
    close_payment_button = (By.XPATH, "//div[contains(@class, 'payment-picker')]//button[contains(@class, 'close-button')]")

    # Mensaje para el conductor
    message_field = (By.ID, 'comment')

    # Manta y pañuelos
    blanket_and_handkerchiefs_switch = (
        By.XPATH,
        "//div[contains(@class, 'r-sw-label') and contains(text(), 'Blanket')]/parent::div//span[contains(@class, 'slider')]"
    )
    blanket_and_handkerchiefs_checkbox = (
        By.XPATH,
        "//div[contains(@class, 'r-sw-label') and contains(text(), 'Blanket')]/parent::div//input"
    )

    # Helado
    ice_cream_plus_button = (
        By.XPATH,
        "//div[contains(@class, 'r-counter-label') and contains(text(), 'Ice cream')]/parent::div//div[@class='counter-plus']"
    )
    ice_cream_counter_value = (
        By.XPATH,
        "//div[contains(@class, 'r-counter-label') and contains(text(), 'Ice cream')]/parent::div//div[@class='counter-value']"
    )

    # Pedir el taxi / modal de búsqueda
    order_button = (By.CLASS_NAME, 'smart-button')
    car_search_modal = (By.CLASS_NAME, 'order-header-title')
    driver_info = (By.CLASS_NAME, 'order-button')

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    # --- Dirección (ejemplo) ---
    def set_from(self, from_address):
        self.driver.find_element(*self.from_field).send_keys(from_address)

    def set_to(self, to_address):
        self.driver.find_element(*self.to_field).send_keys(to_address)

    def get_from(self):
        return self.driver.find_element(*self.from_field).get_property('value')

    def get_to(self):
        return self.driver.find_element(*self.to_field).get_property('value')

    def set_route(self, from_address, to_address):
        self.wait.until(EC.visibility_of_element_located(self.from_field))
        self.set_from(from_address)
        self.set_to(to_address)

    def click_call_taxi(self):
        self.wait.until(EC.element_to_be_clickable(self.call_taxi_button)).click()

    # --- Tarifa Comfort ---
    def select_comfort_tariff(self):
        self.wait.until(EC.element_to_be_clickable(self.comfort_tariff)).click()

    def is_comfort_selected(self):
        element = self.driver.find_element(
            By.XPATH,
            "//div[@class='tcard-title' and text()='Comfort']/ancestor::div[contains(@class, 'tcard')]"
        )
        return 'active' in element.get_attribute('class')

    # --- Teléfono ---
    def fill_phone_number(self, phone_number):
        self.wait.until(EC.element_to_be_clickable(self.phone_button)).click()
        self.wait.until(EC.visibility_of_element_located(self.phone_field)).send_keys(phone_number)
        self.driver.find_element(*self.next_button).click()
        code = retrieve_phone_code(self.driver)
        self.wait.until(EC.visibility_of_element_located(self.code_field)).send_keys(code)
        self.driver.find_element(*self.confirm_phone_button).click()

    def get_phone_number(self):
        return self.driver.find_element(By.CLASS_NAME, 'np-text').text

    # --- Tarjeta de crédito ---
    def add_credit_card(self, card_number, card_code):
        self.wait.until(EC.element_to_be_clickable(self.payment_method_button)).click()
        self.wait.until(EC.element_to_be_clickable(self.add_card_button)).click()
        self.wait.until(EC.visibility_of_element_located(self.card_number_field)).send_keys(card_number)
        code_input = self.driver.find_element(*self.card_code_field)
        code_input.send_keys(card_code)
        # El botón 'link' no se activa hasta que el campo CVV pierde el foco -> simulamos TAB
        code_input.send_keys(Keys.TAB)
        self.wait.until(EC.element_to_be_clickable(self.add_card_link_button)).click()
        self.wait.until(EC.element_to_be_clickable(self.close_payment_button)).click()

    def get_payment_method(self):
        return self.driver.find_element(By.CLASS_NAME, 'pp-value-text').text

    # --- Mensaje para el conductor ---
    def write_message_for_driver(self, message):
        self.wait.until(EC.visibility_of_element_located(self.message_field)).send_keys(message)

    def get_message_for_driver(self):
        return self.driver.find_element(*self.message_field).get_property('value')

    # --- Manta y pañuelos ---
    def order_blanket_and_handkerchiefs(self):
        self.wait.until(EC.element_to_be_clickable(self.blanket_and_handkerchiefs_switch)).click()

    def get_blanket_and_handkerchiefs(self):
        return self.driver.find_element(*self.blanket_and_handkerchiefs_checkbox).is_selected()

    # --- Helado ---
    def order_ice_creams(self, quantity=2):
        for _ in range(quantity):
            self.wait.until(EC.element_to_be_clickable(self.ice_cream_plus_button)).click()

    def get_ice_cream_count(self):
        return int(self.driver.find_element(*self.ice_cream_counter_value).text)

    # --- Pedir taxi ---
    def click_order_button(self):
        self.wait.until(EC.element_to_be_clickable(self.order_button)).click()

    def is_car_search_modal_visible(self):
        return self.wait.until(EC.visibility_of_element_located(self.car_search_modal)).is_displayed()


class TestUrbanRoutes:

    driver = None

    @classmethod
    def setup_class(cls):
        # Habilitamos el registro de rendimiento (necesario para recuperar el código de confirmación del teléfono).
        # Sintaxis Selenium 4 (el 'desired_capabilities' del template quedó obsoleto).
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        cls.driver = webdriver.Chrome(options=options)

    def test_set_route(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.set_route(data.address_from, data.address_to)
        assert routes_page.get_from() == data.address_from
        assert routes_page.get_to() == data.address_to

    def test_select_comfort_tariff(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.click_call_taxi()
        routes_page.select_comfort_tariff()
        assert routes_page.is_comfort_selected()

    def test_fill_phone_number(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.fill_phone_number(data.phone_number)
        assert routes_page.get_phone_number() == data.phone_number

    def test_add_credit_card(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.add_credit_card(data.card_number, data.card_code)
        assert routes_page.get_payment_method() == 'Card'

    def test_write_message_for_driver(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.write_message_for_driver(data.message_for_driver)
        assert routes_page.get_message_for_driver() == data.message_for_driver

    def test_order_blanket_and_handkerchiefs(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.order_blanket_and_handkerchiefs()
        assert routes_page.get_blanket_and_handkerchiefs() is True

    def test_order_two_ice_creams(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.order_ice_creams(2)
        assert routes_page.get_ice_cream_count() == 2

    def test_car_search_modal_appears(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.click_order_button()
        assert routes_page.is_car_search_modal_visible()

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()
