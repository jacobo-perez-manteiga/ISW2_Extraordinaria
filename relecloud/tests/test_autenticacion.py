from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from relecloud.models import Cruise, Destination


class TestAccesibilidadPaginasAuth(TestCase):

    def test_pagina_login_devuelve_200(self):
        response = self.client.get(reverse('account_login'))
        self.assertEqual(response.status_code, 200)

    def test_pagina_signup_devuelve_200(self):
        response = self.client.get(reverse('account_signup'))
        self.assertEqual(response.status_code, 200)

    def test_pagina_logout_devuelve_200_con_sesion_activa(self):
        User.objects.create_user(username='tester', password='Pass1234!')
        self.client.login(username='tester', password='Pass1234!')
        response = self.client.get(reverse('account_logout'))
        self.assertEqual(response.status_code, 200)


class TestTemplatesPaginasAuth(TestCase):

    def test_login_usa_template_base(self):
        response = self.client.get(reverse('account_login'))
        self.assertTemplateUsed(response, 'base.html')

    def test_login_contiene_marca_relecloud(self):
        response = self.client.get(reverse('account_login'))
        self.assertContains(response, 'ReleCloud Space Tourism')

    def test_signup_usa_template_base(self):
        response = self.client.get(reverse('account_signup'))
        self.assertTemplateUsed(response, 'base.html')

    def test_signup_contiene_marca_relecloud(self):
        response = self.client.get(reverse('account_signup'))
        self.assertContains(response, 'ReleCloud Space Tourism')


class TestNavbarSegunEstadoSesion(TestCase):

    def test_navbar_muestra_enlace_login_sin_sesion(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, reverse('account_login'))

    def test_navbar_muestra_enlace_signup_sin_sesion(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, reverse('account_signup'))

    def test_navbar_muestra_nombre_usuario_con_sesion(self):
        User.objects.create_user(username='astronauta', password='Cosmos99!')
        self.client.login(username='astronauta', password='Cosmos99!')
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'astronauta')

    def test_navbar_muestra_opcion_logout_con_sesion(self):
        User.objects.create_user(username='astronauta', password='Cosmos99!')
        self.client.login(username='astronauta', password='Cosmos99!')
        response = self.client.get(reverse('index'))
        self.assertContains(response, reverse('account_logout'))


class TestFlujoAutenticacion(TestCase):

    def test_registro_crea_usuario_en_base_de_datos(self):
        self.client.post(reverse('account_signup'), {
            'username': 'cosmonauta',
            'password1': 'Estrella42!',
            'password2': 'Estrella42!',
        })
        self.assertTrue(User.objects.filter(username='cosmonauta').exists())

    def test_login_con_credenciales_correctas_autentica_al_usuario(self):
        User.objects.create_user(username='cosmonauta', password='Estrella42!')
        response = self.client.post(reverse('account_login'), {
            'login': 'cosmonauta',
            'password': 'Estrella42!',
        }, follow=True)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_con_contrasena_erronea_no_autentica(self):
        User.objects.create_user(username='cosmonauta', password='Estrella42!')
        self.client.post(reverse('account_login'), {
            'login': 'cosmonauta',
            'password': 'ClaveEquivocada99',
        })
        response = self.client.get(reverse('index'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_cierra_la_sesion_activa(self):
        User.objects.create_user(username='cosmonauta', password='Estrella42!')
        self.client.login(username='cosmonauta', password='Estrella42!')
        self.client.post(reverse('account_logout'))
        response = self.client.get(reverse('index'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class TestRedireccionVistasSinAutenticar(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.destino = Destination.objects.create(
            name='Saturno', description='Planeta de los anillos'
        )
        cls.crucero = Cruise.objects.create(
            name='Crucero Saturno', description='Viaje a los anillos de Saturno'
        )

    def test_resena_destino_sin_sesion_redirige_a_login(self):
        url = reverse('review_destination', kwargs={'destination_id': self.destino.pk})
        response = self.client.get(url)
        login_url = reverse('account_login')
        self.assertRedirects(
            response,
            f'{login_url}?next={url}',
            fetch_redirect_response=False,
        )

    def test_resena_crucero_sin_sesion_redirige_a_login(self):
        url = reverse('review_cruise', kwargs={'cruise_id': self.crucero.pk})
        response = self.client.get(url)
        login_url = reverse('account_login')
        self.assertRedirects(
            response,
            f'{login_url}?next={url}',
            fetch_redirect_response=False,
        )
