from django.test import TestCase, override_settings
from django.urls import reverse
from django.core import mail
from unittest.mock import patch

from relecloud.models import Cruise, InfoRequest


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PruebasEnvioEmailInfoRequest(TestCase):

    def setUp(self):
        self.cruise = Cruise.objects.create(name='Crucero Prueba', description='Crucero de prueba')

    def test_envio_valido_guarda_y_envia_email(self):
        data = {
            'name': 'juan',
            'email': 'juan@example.com',
            'cruise': str(self.cruise.pk),
            'notes': 'consulta de prueba'
        }
        response = self.client.post(reverse('info_request'), data, follow=True)

        self.assertEqual(InfoRequest.objects.count(), 1)

        self.assertEqual(len(mail.outbox), 1)
        enviado = mail.outbox[0]
        subject_lower = enviado.subject.lower()
        self.assertIn('informacion', subject_lower)
        self.assertIn('recibida', subject_lower)
        self.assertIn(self.cruise.name.lower(), subject_lower)

    def test_email_invalido_no_guarda_muestra_error(self):
        data = {
            'name': 'pepe',
            'email': 'no email',
            'cruise': str(self.cruise.pk),
            'notes': 'email invalido prueba'
        }
        response = self.client.post(reverse('info_request'), data)

        self.assertEqual(InfoRequest.objects.count(), 0)

        form = response.context.get('form')
        self.assertIsNotNone(form)
        self.assertTrue(form.errors)
        self.assertIn('email', form.errors)

    def test_fallo_smtp_persistir_y_mensaje(self):
        data = {
            'name': 'Carlos',
            'email': 'carlos@example.com',
            'cruise': str(self.cruise.pk),
            'notes': 'falla smtp'
        }

        with patch('relecloud.views.send_mail', side_effect=Exception('SMTP fail')):
            response = self.client.post(reverse('info_request'), data, follow=True)

        self.assertEqual(InfoRequest.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)

        messages = list(response.context.get('messages', []))
        self.assertTrue(any('No se pudo enviar el email de confirmacion' in str(m) for m in messages))


class PruebasFormularioInfoRequest_RED(TestCase):

    def test_existe_clase_InfoRequestForm(self):
        from relecloud import forms

        self.assertTrue(
            hasattr(forms, 'InfoRequestForm'),
            'Se esperaba que InfoRequestForm estuviera definido en relecloud.forms'
        )

    def test_vista_usa_form_class(self):
        from relecloud import forms, views

        self.assertTrue(
            hasattr(views.InfoRequestCreate, 'form_class'),
            'Se esperaba que InfoRequestCreate definiera form_class'
        )
        self.assertEqual(
            views.InfoRequestCreate.form_class,
            forms.InfoRequestForm,
            'InfoRequestCreate.form_class debe ser InfoRequestForm'
        )
