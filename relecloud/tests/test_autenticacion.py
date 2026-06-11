from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from relecloud.models import Destination, Cruise


class TestPaginasAutenticacion(TestCase):
    """
    RED: Las páginas de autenticación deben usar el template base de ReleCloud.
    Fallan hasta que se creen los templates personalizados (commit GREEN).
    """

    def test_login_page_usa_template_base(self):
        """La página de login debe contener el navbar de ReleCloud."""
        response = self.client.get(reverse('account_login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ReleCloud Space Tourism')

    def test_signup_page_usa_template_base(self):
        """La página de registro debe contener el navbar de ReleCloud."""
        response = self.client.get(reverse('account_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ReleCloud Space Tourism')

    def test_navbar_incluye_enlace_login_cuando_no_autenticado(self):
        """El navbar debe mostrar enlace a login para usuarios anónimos."""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('account_login'))

    def test_navbar_incluye_enlace_signup_cuando_no_autenticado(self):
        """El navbar debe mostrar enlace a registro para usuarios anónimos."""
        response = self.client.get(reverse('index'))
        self.assertContains(response, reverse('account_signup'))


class TestFlujoRegistroYLogin(TestCase):
    """
    RED: Flujo completo de registro, login y logout con allauth.
    """

    def test_registro_crea_usuario_nuevo(self):
        """El formulario de registro debe crear un nuevo usuario."""
        self.client.post(reverse('account_signup'), {
            'username': 'nuevousuario',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        self.assertTrue(User.objects.filter(username='nuevousuario').exists())

    def test_login_con_credenciales_validas_autentica_usuario(self):
        """Login con credenciales válidas debe autenticar al usuario."""
        User.objects.create_user('testuser', password='TestPass123!')
        response = self.client.post(reverse('account_login'), {
            'login': 'testuser',
            'password': 'TestPass123!',
        }, follow=True)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_con_credenciales_invalidas_no_autentica(self):
        """Login con contraseña incorrecta no debe autenticar."""
        User.objects.create_user('testuser', password='TestPass123!')
        self.client.post(reverse('account_login'), {
            'login': 'testuser',
            'password': 'ContrasenaIncorrecta',
        })
        response = self.client.get(reverse('index'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_cierra_sesion(self):
        """Logout debe terminar la sesión del usuario."""
        User.objects.create_user('testuser', password='TestPass123!')
        self.client.login(username='testuser', password='TestPass123!')
        self.client.post(reverse('account_logout'))
        response = self.client.get(reverse('index'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_navbar_muestra_nombre_usuario_cuando_autenticado(self):
        """El navbar debe mostrar el nombre del usuario autenticado."""
        User.objects.create_user('testuser', password='TestPass123!')
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'testuser')

    def test_navbar_muestra_enlace_logout_cuando_autenticado(self):
        """El navbar debe mostrar enlace de cerrar sesión cuando hay sesión activa."""
        User.objects.create_user('testuser', password='TestPass123!')
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(reverse('index'))
        self.assertContains(response, reverse('account_logout'))


class TestRedireccionSinAutenticar(TestCase):
    """
    RED: Acceder a vistas de reseña sin autenticar redirige a account_login.
    """

    def setUp(self):
        self.destination = Destination.objects.create(
            name='Marte', description='Planeta rojo'
        )
        self.cruise = Cruise.objects.create(
            name='Crucero Marte', description='Viaje a Marte'
        )

    def test_review_destino_sin_auth_redirige_a_account_login(self):
        """GET a la vista de reseña de destino sin autenticar redirige al login."""
        url = reverse('review_destination', kwargs={'destination_id': self.destination.pk})
        response = self.client.get(url)
        expected = f"{reverse('account_login')}?next={url}"
        self.assertRedirects(response, expected, fetch_redirect_response=False)

    def test_review_crucero_sin_auth_redirige_a_account_login(self):
        """GET a la vista de reseña de crucero sin autenticar redirige al login."""
        url = reverse('review_cruise', kwargs={'cruise_id': self.cruise.pk})
        response = self.client.get(url)
        expected = f"{reverse('account_login')}?next={url}"
        self.assertRedirects(response, expected, fetch_redirect_response=False)

    def test_review_destino_login_url_configurado_correctamente(self):
        """ReviewCreateDestination debe usar login_url='account_login'."""
        from relecloud.views import ReviewCreateDestination
        self.assertEqual(ReviewCreateDestination.login_url, 'account_login')

    def test_review_crucero_login_url_configurado_correctamente(self):
        """ReviewCreateCruise debe usar login_url='account_login'."""
        from relecloud.views import ReviewCreateCruise
        self.assertEqual(ReviewCreateCruise.login_url, 'account_login')
