from django.core.exceptions import ValidationError
import os
from PIL import Image

def validate_image_extension(value):
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError(
            f'Extensión de archivo no permitida. Use: {", ".join(valid_extensions)}'
        )

def validate_image_size(value):
    max_mb = 5
    if value.size > max_mb * 1024 * 1024:
        actual_mb = value.size / (1024 * 1024)
        raise ValidationError(
            f'El tamaño máximo permitido es {max_mb}MB. Tamaño actual: {actual_mb:.2f}MB'
        )

def validate_image_dimensions(value):
    try:
        img = Image.open(value)
        width, height = img.size

        if width > 2000 or height > 2000:
            raise ValidationError(
                f'Las dimensiones máximas permitidas son 2000x2000 píxeles. '
                f'Dimensiones actuales: {width}x{height} píxeles'
            )

        if width < 300 or height < 300:
            raise ValidationError(
                f'Las dimensiones mínimas requeridas son 300x300 píxeles. '
                f'Dimensiones actuales: {width}x{height} píxeles'
            )
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError('Formato de imagen inválido o corrupto')
