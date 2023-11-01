# Creación del modelo

En la carpeta [datasets](datasets) se encuentran las fotos .jpeg usadas para prueba para el entrenamiento e implementación del modelo, estas fotos son usadas como base antes de establecer la conexión con la nube. En esta msima carpeta también se encuentra un video tomado para que sea el utilizado para la verificación del video.

En el código de [Modelo.ipynb](Modelo.ipynb) se encuentra el modelo, en el cual se establece el reconocimiento facial a través de la librería face_recognition y la detección de pose con tensorflow, este código es capaz de hacer la predicción de identificación y marcar la pose de las personas en tiempo real.

## Timeline.

**Completado.** Reconocimiento facial y de pose a través de una cámara exterior a un grupo de personas a una distancia adecuada para un salón de clases prueba. 

**Ejecución.** Detección de participación (levantar la mano) e integración de ambos modelos para detectar a la persona que levanta la mano.

**Pendientes.** Conteo de asistencia y participación en tiempo real, así como la integración con la interfaz.
