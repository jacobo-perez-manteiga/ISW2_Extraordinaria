from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class TestRenderizadoTemplateLogin(TestCase):
    """El template de login se renderiza correctamente."""

    def test_pagina_login_devuelve_200(self):
        response = self.client.get(reverse('account_login'))
        self.assertEqual(response.status_code, 200)

    def test_login_usa_template_base(self):
        response = self.client.get(reverse('account_login'))
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'account/login.html')

    def test_login_tiene_titulo_correcto(self):
        response = self.client.get(reverse('account_login'))
        self.assertContains(response, 'ReleCloud - Iniciar sesión')

    def test_login_contiene_formulario_post(self):
        response = self.client.get(reverse('account_login'))
        self.assertContains(response, 'method="post"')
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_login_enlaza_a_signup(self):
        response = self.client.get(reverse('account_login'))
        self.assertContains(response, reverse('account_signup'))


class TestRenderizadoTemplateSignup(TestCase):
    """El template de registro se renderiza correctamente."""

    def test_pagina_signup_devuelve_200(self):
        response = self.client.get(reverse('account_signup'))
        self.assertEqual(response.status_code, 200)

    def test_signup_usa_template_base(self):
        response = self.client.get(reverse('account_signup'))
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'account/signup.html')

    def test_signup_tiene_titulo_correcto(self):
        response = self.client.get(reverse('account_signup'))
        self.assertContains(response, 'ReleCloud - Registrarse')

    def test_signup_contiene_formulario_post(self):
        response = self.client.get(reverse('account_signup'))
        self.assertContains(response, 'method="post"')
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_signup_enlaza_a_login(self):
        response = self.client.get(reverse('account_signup'))
        self.assertContains(response, reverse('account_login'))


class TestRenderizadoTemplateLogout(TestCase):
    """El template de logout se renderiza correctamente."""

    def setUp(self):
        User.objects.create_user(username='tester', password='Pass1234!')
        self.client.login(username='tester', password='Pass1234!')

    def test_pagina_logout_devuelve_200(self):
        response = self.client.get(reverse('account_logout'))
        self.assertEqual(response.status_code, 200)

    def test_logout_usa_template_base(self):
        response = self.client.get(reverse('account_logout'))
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'account/logout.html')

    def test_logout_tiene_titulo_correcto(self):
        response = self.client.get(reverse('account_logout'))
        self.assertContains(response, 'ReleCloud - Cerrar sesión')

    def test_logout_tiene_boton_confirmar(self):
        response = self.client.get(reverse('account_logout'))
        self.assertContains(response, 'btn-danger')

    def test_logout_tiene_enlace_cancelar_al_inicio(self):
        response = self.client.get(reverse('account_logout'))
        self.assertContains(response, reverse('index'))


class TestDisenoVisualTemplates(TestCase):
    """Los templates de autenticación mantienen el diseño visual de ReleCloud."""

    def test_login_contiene_contenedor_responsivo(self):
        """El formulario de login debe estar centrado con columna Bootstrap."""
        response = self.client.get(reverse('account_login'))
        self.assertContains(response, 'col-md-6')

    def test_signup_contiene_contenedor_responsivo(self):
        """El formulario de registro debe estar centrado con columna Bootstrap."""
        response = self.client.get(reverse('account_signup'))
        self.assertContains(response, 'col-md-6')

    def test_login_contiene_estructura_card(self):
        """El formulario de login debe estar envuelto en una card Bootstrap."""
        response = self.client.get(reverse('account_login'))
        self.assertContains(response, 'card-body')

    def test_signup_contiene_estructura_card(self):
        """El formulario de registro debe estar envuelto en una card Bootstrap."""
        response = self.client.get(reverse('account_signup'))
        self.assertContains(response, 'card-body')

    def test_logout_contiene_estructura_card(self):
        """La confirmación de logout debe estar envuelta en una card Bootstrap."""
        User.objects.create_user(username='tester', password='Pass1234!')
        self.client.login(username='tester', password='Pass1234!')
        response = self.client.get(reverse('account_logout'))
        self.assertContains(response, 'card-body')
