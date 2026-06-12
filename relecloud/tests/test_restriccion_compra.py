from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from relecloud.models import Cruise, Destination, Review, Purchase


class TestRestriccionCompraDestino(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('testuser', password='TestPass123!')
        self.destination = Destination.objects.create(
            name='Venus', description='Planeta caliente'
        )
        self.url = reverse('review_destination', kwargs={'destination_id': self.destination.pk})

    def test_usuario_sin_compra_recibe_403_al_resenar_destino(self):
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.post(self.url, {
            'rating': 5, 'title': 'Genial', 'comment': 'Increíble experiencia',
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Review.objects.count(), 0)

    def test_usuario_sin_compra_recibe_403_en_get_destino(self):
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_usuario_con_compra_puede_resenar_destino(self):
        Purchase.objects.create(user=self.user, destination=self.destination)
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.post(self.url, {
            'rating': 5, 'title': 'Genial', 'comment': 'Increíble experiencia',
        })
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.first().user, self.user)

    def test_can_review_falso_para_usuario_sin_compra(self):
        self.client.login(username='testuser', password='TestPass123!')
        url_detail = reverse('destination_detail', kwargs={'pk': self.destination.pk})
        response = self.client.get(url_detail)
        self.assertFalse(response.context['can_review'])

    def test_can_review_verdadero_para_usuario_con_compra_y_sin_resena(self):
        Purchase.objects.create(user=self.user, destination=self.destination)
        self.client.login(username='testuser', password='TestPass123!')
        url_detail = reverse('destination_detail', kwargs={'pk': self.destination.pk})
        response = self.client.get(url_detail)
        self.assertTrue(response.context['can_review'])

    def test_has_purchase_en_contexto_sin_compra(self):
        self.client.login(username='testuser', password='TestPass123!')
        url_detail = reverse('destination_detail', kwargs={'pk': self.destination.pk})
        response = self.client.get(url_detail)
        self.assertFalse(response.context['has_purchase'])

    def test_has_purchase_en_contexto_con_compra(self):
        Purchase.objects.create(user=self.user, destination=self.destination)
        self.client.login(username='testuser', password='TestPass123!')
        url_detail = reverse('destination_detail', kwargs={'pk': self.destination.pk})
        response = self.client.get(url_detail)
        self.assertTrue(response.context['has_purchase'])


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

    def test_usuario_sin_compra_recibe_403_al_resenar_crucero(self):
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.post(self.url, {
            'rating': 5, 'title': 'Genial', 'comment': 'Increíble experiencia',
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Review.objects.count(), 0)

    def test_usuario_sin_compra_recibe_403_en_get_crucero(self):
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_usuario_con_compra_puede_resenar_crucero(self):
        Purchase.objects.create(user=self.user, cruise=self.cruise)
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.post(self.url, {
            'rating': 5, 'title': 'Genial', 'comment': 'Increíble experiencia',
        })
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.first().user, self.user)

    def test_can_review_falso_para_usuario_sin_compra(self):
        self.client.login(username='testuser', password='TestPass123!')
        url_detail = reverse('cruise_detail', kwargs={'pk': self.cruise.pk})
        response = self.client.get(url_detail)
        self.assertFalse(response.context['can_review'])

    def test_can_review_verdadero_para_usuario_con_compra_y_sin_resena(self):
        Purchase.objects.create(user=self.user, cruise=self.cruise)
        self.client.login(username='testuser', password='TestPass123!')
        url_detail = reverse('cruise_detail', kwargs={'pk': self.cruise.pk})
        response = self.client.get(url_detail)
        self.assertTrue(response.context['can_review'])

    def test_has_purchase_en_contexto_sin_compra(self):
        self.client.login(username='testuser', password='TestPass123!')
        url_detail = reverse('cruise_detail', kwargs={'pk': self.cruise.pk})
        response = self.client.get(url_detail)
        self.assertFalse(response.context['has_purchase'])

    def test_has_purchase_en_contexto_con_compra(self):
        Purchase.objects.create(user=self.user, cruise=self.cruise)
        self.client.login(username='testuser', password='TestPass123!')
        url_detail = reverse('cruise_detail', kwargs={'pk': self.cruise.pk})
        response = self.client.get(url_detail)
        self.assertTrue(response.context['has_purchase'])
