# Momento de Retroalimentación: Reto Modelo y Refinamiento

Dentro de dicha carpeta podemos observar que hay distintos archivos y carpetas que fueron utilizadas para la actividad. La actividad buscaba crear un Benchmark de un modelo de reconocimiento facial y después crear otro modelo distinto pero con el mismo objetivo y buscar modificar parámetros para obtener el mejor resultado posible para el objetivo del reto, el cual es identificar alumnos en un aula de clases. Primeramente, se encuentran dos carpetas con diferentes datasets utilizados para ambos modelos:

- [FotosPruebaHaar](FotosPruebaHaar): Dataset utilizado para entrenar el modelo Haar Cascade.
- [FotosPruebaFace_Recog](FotosPruebaFace_Recog): Dataset utilizado para entrenar el modelo face_recognition.

Después, tenemos el archivo [Benchmark.ipynb](Benchmark.ipynb) en donde se tiene el modelo de Haar Cascade, tanto la recolección de datos, el entrenamiento y la ejecución de este. Dicho archivo va de la mano con el [haarcascade_frontalface_default.xml](haarcascade_frontalface_default.xml) el cual es el archivo donde se encuentra el modelo de Haar Cascade.

Luego, se tiene el archivo [FaceRecognitionActividad.ipynb](FaceRecognitionActividad.ipynb). Este archivo cuenta con las pruebas de face_recognition y el modelo. Dentro de este se encuentra cuando tolerance = 0.6 debido a que fue el mejor parámetro para la situación problema.
