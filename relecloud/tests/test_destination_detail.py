from django.test import TestCase
from django.urls import reverse
from relecloud.models import Destination, Review
from django.contrib.auth.models import User


class DestinationDetailContextTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')
        self.user3 = User.objects.create_user(username='user3', password='pass')
        self.destination = Destination.objects.create(name='Destino Test', description='desc')

    def _create_review(self, user, rating):
        return Review.objects.create(
            user=user,
            destination=self.destination,
            rating=rating,
            title='Titulo',
            comment='Comentario',
        )

    def test_contexto_contiene_average_rating_correcto(self):
        self._create_review(self.user1, 4)
        self._create_review(self.user2, 2)
        self._create_review(self.user3, 3)

        response = self.client.get(reverse('destination_detail', kwargs={'pk': self.destination.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['average_rating'], 3.0)

    def test_contexto_contiene_review_count_correcto(self):
        self._create_review(self.user1, 5)
        self._create_review(self.user2, 3)

        response = self.client.get(reverse('destination_detail', kwargs={'pk': self.destination.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['review_count'], 2)

    def test_destino_sin_reviews_average_rating_cero(self):
        response = self.client.get(reverse('destination_detail', kwargs={'pk': self.destination.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['average_rating'], 0)
        self.assertEqual(response.context['review_count'], 0)

    def test_template_muestra_sin_resenas_si_no_hay_reviews(self):
        response = self.client.get(reverse('destination_detail', kwargs={'pk': self.destination.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sin reseñas aún')