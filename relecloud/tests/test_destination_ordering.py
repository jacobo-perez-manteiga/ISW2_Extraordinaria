from django.test import TestCase
from django.urls import reverse
from relecloud.models import Destination, Review
from django.contrib.auth.models import User


class DestinationOrderingTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')
        self.user3 = User.objects.create_user(username='user3', password='pass')

    def _create_review(self, user, destination, rating):
        return Review.objects.create(
            user=user,
            destination=destination,
            rating=rating,
            title='Titulo',
            comment='Comentario',
        )

    def test_destino_mas_reviews_aparece_primero(self):
        dest_popular = Destination.objects.create(name='Destino Popular', description='desc')
        dest_poco = Destination.objects.create(name='Destino Poco Popular', description='desc')

        self._create_review(self.user1, dest_popular, 4)
        self._create_review(self.user2, dest_popular, 3)
        self._create_review(self.user3, dest_poco, 5)

        response = self.client.get(reverse('destinations'))
        self.assertEqual(response.status_code, 200)
        destinations = list(response.context['destinations'])
        self.assertEqual(destinations[0].id, dest_popular.id)

    def test_empate_reviews_orden_por_media(self):
        dest_alta_media = Destination.objects.create(name='Alta Media', description='desc')
        dest_baja_media = Destination.objects.create(name='Baja Media', description='desc')

        self._create_review(self.user1, dest_alta_media, 5)
        self._create_review(self.user2, dest_baja_media, 2)

        response = self.client.get(reverse('destinations'))
        self.assertEqual(response.status_code, 200)
        destinations = list(response.context['destinations'])
        self.assertEqual(destinations[0].id, dest_alta_media.id)

    def test_destinos_sin_reviews_aparecen_al_final(self):
        dest_con_reviews = Destination.objects.create(name='Con Reviews', description='desc')
        dest_sin_reviews = Destination.objects.create(name='Sin Reviews', description='desc')

        self._create_review(self.user1, dest_con_reviews, 4)

        response = self.client.get(reverse('destinations'))
        self.assertEqual(response.status_code, 200)
        destinations = list(response.context['destinations'])
        self.assertEqual(destinations[-1].id, dest_sin_reviews.id)

    def test_contexto_contiene_anotaciones(self):
        dest = Destination.objects.create(name='Destino Test', description='desc')
        self._create_review(self.user1, dest, 3)

        response = self.client.get(reverse('destinations'))
        self.assertEqual(response.status_code, 200)
        destinations = list(response.context['destinations'])
        for d in destinations:
            self.assertTrue(hasattr(d, 'review_count'))
            self.assertTrue(hasattr(d, 'avg_rating'))
