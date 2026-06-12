from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from relecloud.models import Cruise, Destination, Review


class TestRestriccionCompraDestino(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('testuser', password='TestPass123!')
        self.destination = Destination.objects.create(
            name='Venus', description='Planeta caliente'
        )
        self.url = reverse('review_destination', kwargs={'destination_id': self.destination.pk})

    def test_usuario_sin_login_no_puede_resenar_destino(self):
        response = self.client.post(self.url, {
            'rating': 5, 'title': 'Genial', 'comment': 'Increible experiencia',
        })
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(Review.objects.count(), 0)

    def test_usuario_registrado_puede_resenar_destino(self):
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.post(self.url, {
            'rating': 5, 'title': 'Genial', 'comment': 'Increible experiencia',
        })
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.first().user, self.user)

    def test_usuario_no_puede_resenar_destino_dos_veces(self):
        self.client.login(username='testuser', password='TestPass123!')
        self.client.post(self.url, {
            'rating': 5, 'title': 'Genial', 'comment': 'Increible experiencia',
        })
        response = self.client.post(self.url, {
            'rating': 3, 'title': 'Ok', 'comment': 'Normal',
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Review.objects.count(), 1)

    def test_can_review_verdadero_para_usuario_sin_resena(self):
        self.client.login(username='testuser', password='TestPass123!')
        url_detail = reverse('destination_detail', kwargs={'pk': self.destination.pk})
        response = self.client.get(url_detail)
        self.assertTrue(response.context['can_review'])

    def test_can_review_falso_para_usuario_con_resena(self):
        Review.objects.create(
            user=self.user, destination=self.destination,
            rating=5, title='Genial', comment='Increible'
        )
        self.client.login(username='testuser', password='TestPass123!')
        url_detail = reverse('destination_detail', kwargs={'pk': self.destination.pk})
        response = self.client.get(url_detail)
        self.assertFalse(response.context['can_review'])

    def test_can_review_falso_para_usuario_no_autenticado(self):
        url_detail = reverse('destination_detail', kwargs={'pk': self.destination.pk})
        response = self.client.get(url_detail)
        self.assertFalse(response.context['can_review'])


class TestRestriccionCompraCrucero(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('testuser', password='TestPass123!')
        self.destination = Destination.objects.create(
            name='Venus', description='Planeta caliente'
        )
        self.cruise = Cruise.objects.create(
            name='Crucero Venus', description='Viaje a Venus'
        )
        self.cruise.destinations.add(self.destination)
        self.url = reverse('review_cruise', kwargs={'cruise_id': self.cruise.pk})

    def test_usuario_sin_login_no_puede_resenar_crucero(self):
        response = self.client.post(self.url, {
            'rating': 5, 'title': 'Genial', 'comment': 'Increible experiencia',
        })
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(Review.objects.count(), 0)

    def test_usuario_registrado_puede_resenar_crucero(self):
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.post(self.url, {
            'rating': 5, 'title': 'Genial', 'comment': 'Increible experiencia',
        })
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.first().user, self.user)

    def test_usuario_no_puede_resenar_crucero_dos_veces(self):
        self.client.login(username='testuser', password='TestPass123!')
        self.client.post(self.url, {
            'rating': 5, 'title': 'Genial', 'comment': 'Increible experiencia',
        })
        response = self.client.post(self.url, {
            'rating': 3, 'title': 'Ok', 'comment': 'Normal',
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Review.objects.count(), 1)

    def test_can_review_verdadero_para_usuario_sin_resena(self):
        self.client.login(username='testuser', password='TestPass123!')
        url_detail = reverse('cruise_detail', kwargs={'pk': self.cruise.pk})
        response = self.client.get(url_detail)
        self.assertTrue(response.context['can_review'])

    def test_can_review_falso_para_usuario_con_resena(self):
        Review.objects.create(
            user=self.user, cruise=self.cruise,
            rating=5, title='Genial', comment='Increible'
        )
        self.client.login(username='testuser', password='TestPass123!')
        url_detail = reverse('cruise_detail', kwargs={'pk': self.cruise.pk})
        response = self.client.get(url_detail)
        self.assertFalse(response.context['can_review'])

    def test_can_review_falso_para_usuario_no_autenticado(self):
        url_detail = reverse('cruise_detail', kwargs={'pk': self.cruise.pk})
        response = self.client.get(url_detail)
        self.assertFalse(response.context['can_review'])