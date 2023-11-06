# Interfaz

Se tienen distintos códigos necesarios para la creación de usuarios e ingreso a la plataforma. El código [Interfaz](InterfazSegura.py) contiene la pantalla principal para el LogIn o SignUp, así como la obtención de foto. Este código está conectado con Google Storage y Firestore. 

En los códigos de plataformas de [docente](plataforma_docente.py) y [estudiante](plataforma_estudiante.py) se encuentran las plantillas para las plataformas correspondientes. La plataforma principal de registro te dirige automáticamente a la plataforma correspondiente a tu rol en la institución. 

Algunas claves y llaves no se comparten por motivos de seguridad de la información. 

## Timeline.

**Completado.** Identificación de credenciales, obtención de fotografías confiables para el entrenamiento del modelo, conexión con la nube (Cloud Storage y Firestore), creación de cuentas y dirigir a la plataforma correspondiente (estudiante o docente)

**Ejecución.** Configuración de las funciones y atributos de las pestañas de navegación en las plataformas y cursos relacionados a cada cuenta. 

**Pendientes.** Conexión con el modelo para la generación de visualizaciones.
