from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from relecloud.models import Destination, Cruise, Review


class TestVisualizacionResenasDestino(TestCase):
    """
    RED: Las reseñas y valoración media se muestran correctamente en el detalle de destino.
    """

    def setUp(self):
        self.user1 = User.objects.create_user('usuario1', password='TestPass123!')
        self.user2 = User.objects.create_user('usuario2', password='TestPass123!')
        self.destination = Destination.objects.create(
            name='Saturno', description='El planeta de los anillos'
        )
        self.url = reverse('destination_detail', kwargs={'pk': self.destination.pk})

    def test_detalle_destino_muestra_lista_de_resenas(self):
        """El detalle de destino muestra las reseñas existentes."""
        Review.objects.create(
            user=self.user1, destination=self.destination,
            rating=5, title='Espectacular', comment='Una maravilla'
        )
        response = self.client.get(self.url)
        self.assertContains(response, 'Espectacular')
        self.assertContains(response, 'Una maravilla')
        self.assertContains(response, 'usuario1')

    def test_detalle_destino_muestra_multiples_resenas(self):
        """El detalle de destino muestra todas las reseñas de distintos usuarios."""
        Review.objects.create(
            user=self.user1, destination=self.destination,
            rating=5, title='Increíble', comment='Me encantó'
        )
        Review.objects.create(
            user=self.user2, destination=self.destination,
            rating=3, title='Aceptable', comment='Estuvo bien'
        )
        response = self.client.get(self.url)
        self.assertContains(response, 'Increíble')
        self.assertContains(response, 'Aceptable')

    def test_detalle_destino_muestra_valoracion_media(self):
        """El detalle de destino muestra la puntuación media correctamente."""
        Review.objects.create(
            user=self.user1, destination=self.destination,
            rating=4, title='Bien', comment='Bien'
        )
        Review.objects.create(
            user=self.user2, destination=self.destination,
            rating=2, title='Regular', comment='Regular'
        )
        response = self.client.get(self.url)
        # Media de 4 y 2 = 3.0 (con LANGUAGE_CODE='es' se muestra como '3,0')
        self.assertContains(response, '3,0')

    def test_detalle_destino_sin_resenas_muestra_mensaje(self):
        """Sin reseñas se muestra el mensaje 'No hay reseñas aún'."""
        response = self.client.get(self.url)
        self.assertContains(response, 'No hay reseñas aún')

    def test_contexto_average_rating_es_correcto(self):
        """El contexto average_rating refleja la media real de las reseñas."""
        Review.objects.create(
            user=self.user1, destination=self.destination,
            rating=5, title='A', comment='A'
        )
        Review.objects.create(
            user=self.user2, destination=self.destination,
            rating=3, title='B', comment='B'
        )
        response = self.client.get(self.url)
        self.assertEqual(response.context['average_rating'], 4.0)

    def test_contexto_review_count_es_correcto(self):
        """El contexto review_count refleja el número real de reseñas."""
        Review.objects.create(
            user=self.user1, destination=self.destination,
            rating=5, title='A', comment='A'
        )
        response = self.client.get(self.url)
        self.assertEqual(response.context['review_count'], 1)

    def test_contexto_sin_resenas_average_rating_es_cero(self):
        """Sin reseñas, average_rating es 0 y review_count es 0."""
        response = self.client.get(self.url)
        self.assertEqual(response.context['average_rating'], 0)
        self.assertEqual(response.context['review_count'], 0)


class TestVisualizacionResenasCrucero(TestCase):
    """
    RED: Las reseñas y valoración media se muestran correctamente en el detalle de crucero.
    """

    def setUp(self):
        self.user1 = User.objects.create_user('usuario1', password='TestPass123!')
        self.user2 = User.objects.create_user('usuario2', password='TestPass123!')
        self.cruise = Cruise.objects.create(
            name='Crucero Saturno', description='Viaje a Saturno'
        )
        self.url = reverse('cruise_detail', kwargs={'pk': self.cruise.pk})

    def test_detalle_crucero_muestra_lista_de_resenas(self):
        """El detalle de crucero muestra las reseñas existentes."""
        Review.objects.create(
            user=self.user1, cruise=self.cruise,
            rating=5, title='Fantástico', comment='Lo mejor'
        )
        response = self.client.get(self.url)
        self.assertContains(response, 'Fantástico')
        self.assertContains(response, 'Lo mejor')
        self.assertContains(response, 'usuario1')

    def test_detalle_crucero_muestra_valoracion_media(self):
        """El detalle de crucero muestra la puntuación media correctamente."""
        Review.objects.create(
            user=self.user1, cruise=self.cruise,
            rating=5, title='Genial', comment='Genial'
        )
        Review.objects.create(
            user=self.user2, cruise=self.cruise,
            rating=1, title='Horrible', comment='Horrible'
        )
        response = self.client.get(self.url)
        # Media de 5 y 1 = 3.0 (con LANGUAGE_CODE='es' se muestra como '3,0')
        self.assertContains(response, '3,0')

    def test_detalle_crucero_sin_resenas_muestra_mensaje(self):
        """Sin reseñas se muestra el mensaje 'No hay reseñas aún'."""
        response = self.client.get(self.url)
        self.assertContains(response, 'No hay reseñas aún')

    def test_contexto_average_rating_crucero_es_correcto(self):
        """El contexto average_rating del crucero refleja la media real."""
        Review.objects.create(
            user=self.user1, cruise=self.cruise,
            rating=4, title='A', comment='A'
        )
        Review.objects.create(
            user=self.user2, cruise=self.cruise,
            rating=2, title='B', comment='B'
        )
        response = self.client.get(self.url)
        self.assertEqual(response.context['average_rating'], 3.0)


class TestVisualizacionRatingEnListaDestinos(TestCase):
    """
    RED: La lista de destinos muestra la valoración media junto a cada destino.
    """

    def setUp(self):
        self.user1 = User.objects.create_user('usuario1', password='TestPass123!')
        self.user2 = User.objects.create_user('usuario2', password='TestPass123!')
        self.destination = Destination.objects.create(
            name='Júpiter', description='El gigante gaseoso'
        )
        self.url = reverse('destinations')

    def test_lista_destinos_muestra_badge_rating_con_resenas(self):
        """La lista de destinos muestra el badge de rating cuando hay reseñas."""
        Review.objects.create(
            user=self.user1, destination=self.destination,
            rating=4, title='A', comment='A'
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # Con LANGUAGE_CODE='es' el float se muestra con coma decimal
        self.assertContains(response, '4,0')

    def test_lista_destinos_muestra_badge_sin_valoraciones_sin_resenas(self):
        """La lista de destinos muestra 'Sin valoraciones' cuando no hay reseñas."""
        response = self.client.get(self.url)
        self.assertContains(response, 'Sin valoraciones')

    def test_lista_destinos_muestra_numero_de_resenas(self):
        """La lista de destinos muestra el número de reseñas junto al rating."""
        Review.objects.create(
            user=self.user1, destination=self.destination,
            rating=5, title='A', comment='A'
        )
        Review.objects.create(
            user=self.user2, destination=self.destination,
            rating=3, title='B', comment='B'
        )
        response = self.client.get(self.url)
        self.assertContains(response, '2 reseñas')

    def test_lista_destinos_ordena_por_popularidad(self):
        """Los destinos con más reseñas aparecen primero en la lista."""
        destino_popular = Destination.objects.create(
            name='Venus', description='El planeta caliente'
        )
        Review.objects.create(
            user=self.user1, destination=destino_popular,
            rating=5, title='A', comment='A'
        )
        Review.objects.create(
            user=self.user2, destination=destino_popular,
            rating=4, title='B', comment='B'
        )
        response = self.client.get(self.url)
        destinos = list(response.context['destinations'])
        self.assertEqual(destinos[0].name, 'Venus')
