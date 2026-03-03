from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

class SecurityRegressionTests(StaticLiveServerTestCase):
    fixtures = ['testdb.json']  # Càrrega de dades (Punt 2.2.2)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        opts.add_argument("--headless")  # mode Headless (Punt 2.2.1)
        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_role_restriction(self):
        """AUDITORIA: L'analista no ha d'entrar a /admin/"""
        
        # 1. Anem directament al login de l'administració de Django
        # Aquesta URL és més robusta que /accounts/login/
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login/'))
        
        # 2. Emplenem els camps (Django Admin usa name="username" i name="password")
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys("Analista1")
        
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys("Abcd.1234")
        
        # 3. Fem clic al botó de login (a l'admin de Django és un <input type="submit">)
        self.selenium.find_element(By.XPATH, '//input[@type="submit"]').click()
        
        # 4. Intentem forçar la URL d'administració
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/'))
        
        # 5. ASSERT de Seguretat (Fase GREEN)
        # Com que Analista1 té is_staff=False al JSON, Django NO el deixarà entrar.
        # El títol de la pàgina NO ha de ser el de l'administració.
        self.assertNotEqual(self.selenium.title, "Site administration | Django site admin")