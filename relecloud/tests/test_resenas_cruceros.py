from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from relecloud.models import Cruise, Destination, Review


class TestCrearResenaCrucero(TestCase):
    """
    RED: Lógica de creación de reseñas para cruceros.
    """

    def setUp(self):
        self.user = User.objects.create_user('testuser', password='TestPass123!')
        self.destination = Destination.objects.create(
            name='Marte', description='Planeta rojo'
        )
        self.cruise = Cruise.objects.create(
            name='Crucero Marte', description='Viaje al planeta rojo'
        )
        self.cruise.destinations.add(self.destination)
        self.url = reverse('review_cruise', kwargs={'cruise_id': self.cruise.pk})

    def test_usuario_autenticado_puede_crear_resena(self):
        """Un usuario autenticado puede enviar una reseña para un crucero."""
        self.client.login(username='testuser', password='TestPass123!')
        self.client.post(self.url, {
            'rating': 5,
            'title': 'Viaje increíble',
            'comment': 'Lo mejor que he hecho en mi vida',
        })
        self.assertEqual(Review.objects.count(), 1)
        resena = Review.objects.first()
        self.assertEqual(resena.user, self.user)
        self.assertEqual(resena.cruise, self.cruise)
        self.assertEqual(resena.rating, 5)

    def test_crear_resena_redirige_a_detalle_crucero(self):
        """Tras crear una reseña se redirige a la página del crucero."""
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.post(self.url, {
            'rating': 4,
            'title': 'Muy bien',
            'comment': 'Me gustó mucho',
        })
        self.assertRedirects(
            response,
            reverse('cruise_detail', kwargs={'pk': self.cruise.pk}),
            fetch_redirect_response=False
        )

    def test_resena_duplicada_devuelve_403(self):
        """Un usuario no puede crear dos reseñas para el mismo crucero."""
        Review.objects.create(
            user=self.user,
            cruise=self.cruise,
            rating=3,
            title='Primera reseña',
            comment='Ya dejé una reseña'
        )
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.post(self.url, {
            'rating': 5,
            'title': 'Segunda reseña',
            'comment': 'Intento duplicar',
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Review.objects.count(), 1)

    def test_resena_sin_autenticar_redirige_a_login(self):
        """Un usuario no autenticado es redirigido al login al intentar reseñar."""
        response = self.client.post(self.url, {
            'rating': 5,
            'title': 'Sin login',
            'comment': 'No debería funcionar',
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('account_login'), response['Location'])
        self.assertEqual(Review.objects.count(), 0)

    def test_resena_con_rating_invalido_no_se_guarda(self):
        """Un rating fuera de rango no debe guardarse."""
        self.client.login(username='testuser', password='TestPass123!')
        self.client.post(self.url, {
            'rating': 6,
            'title': 'Rating inválido',
            'comment': 'No debería guardarse',
        })
        self.assertEqual(Review.objects.count(), 0)


class TestVistaDetalleCruceroResenas(TestCase):
    """
    RED: La página de detalle de crucero muestra la sección de reseñas correctamente.
    """

    def setUp(self):
        self.user = User.objects.create_user('testuser', password='TestPass123!')
        self.cruise = Cruise.objects.create(
            name='Crucero Luna', description='Viaje a la Luna'
        )
        self.url = reverse('cruise_detail', kwargs={'pk': self.cruise.pk})

    def test_usuario_autenticado_sin_resena_ve_boton_dejar_resena(self):
        """Usuario autenticado sin reseña previa ve el botón para dejar una reseña."""
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('review_cruise', kwargs={'cruise_id': self.cruise.pk}))

    def test_usuario_no_autenticado_ve_botones_login_y_registro(self):
        """Usuario no autenticado ve botones de login y registro en la sección de reseñas."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('account_login'))
        self.assertContains(response, reverse('account_signup'))

    def test_usuario_no_autenticado_ve_parametro_next(self):
        """Los botones de login/registro incluyen ?next= con la URL actual."""
        response = self.client.get(self.url)
        self.assertContains(response, f'?next={self.url}')

    def test_usuario_con_resena_previa_no_ve_boton_nueva_resena(self):
        """Usuario que ya dejó reseña no ve el botón para crear otra."""
        Review.objects.create(
            user=self.user,
            cruise=self.cruise,
            rating=4,
            title='Mi reseña',
            comment='Ya la dejé'
        )
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(self.url)
        review_url = reverse('review_cruise', kwargs={'cruise_id': self.cruise.pk})
        self.assertNotContains(response, f'href="{review_url}"')

    def test_contexto_can_review_es_true_para_usuario_sin_resena(self):
        """El contexto can_review es True para usuario autenticado sin reseña."""
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(self.url)
        self.assertTrue(response.context['can_review'])

    def test_contexto_can_review_es_false_para_usuario_con_resena(self):
        """El contexto can_review es False para usuario que ya dejó reseña."""
        Review.objects.create(
            user=self.user,
            cruise=self.cruise,
            rating=3,
            title='Reseña existente',
            comment='Ya existe'
        )
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(self.url)
        self.assertFalse(response.context['can_review'])
        self.assertIsNotNone(response.context['user_review'])
