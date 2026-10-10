Extractor de ofertas de empleo y notificador de Telegram (backend en Docker)
Un sistema automatizado de extracción de datos (Web Scraping) de grado de producción diseñado para monitorear ofertas de empleo orientadas al perfil Python, enfocado exclusivamente en mercados hispanohablantes (Paraguay, España, México, Argentina, Colombia y Chile). El sistema almacena las vacantes en una base de datos relacional para evitar duplicados y envía notificaciones en tiempo real mediante un bot de Telegram.

Todo el entorno está 100% contenerizado con Docker, lo que garantiza su ejecución perfecta en cualquier sistema operativo sin necesidad de instalar dependencias locales complejas.

Arquitectura del Proyecto
Este proyecto está diseñado bajo una arquitectura modular y asíncrona:

Infraestructura Contenerizada: Utiliza Docker y Docker Compose para orquestar dos servicios: una base de datos persistente y el script extractor. El contenedor de Python aprovecha la caché de capas de Docker para compilaciones ultrarrápidas y se cierra automáticamente al finalizar su tarea para no consumir recursos (RAM/CPU) en estado de reposo.

Extracción Inteligente (Scraping): Combina Playwright para la emulación segura de navegación y BeautifulSoup4 para el parseo del DOM. Implementa extracción basada en IDs únicos para blindar el sistema contra URLs dinámicas de rastreo.

Filtrado Avanzado: Cuenta con un motor de validación semántica que descarta automáticamente puestos enfocados a perfiles corporativos exclusivamente Senior/Lead o que exijan de forma explícita inglés avanzado, optimizando la calidad de las alertas para el usuario.

Almacenamiento (Persistencia): Conectado a un contenedor dedicado de PostgreSQL mediante un ORM (SQLAlchemy). Utiliza la instrucción de inserción segura ON CONFLICT DO NOTHING basada en restricciones de clave única (UNIQUE). Cuenta con healthchecks para garantizar que el scraper espere a que la base de datos esté completamente inicializada.

Notificaciones (API): Conexión nativa con la API de Telegram. Agrupa los mensajes en lotes (batching) para respetar los límites de la plataforma (rate limits).

Tecnologías Utilizadas (Tech Stack)
Infraestructura: Docker, Docker Compose

Lenguaje: Python 3.10+ (Programación Asíncrona / Asyncio)

Extracción de datos web: Playwright, BeautifulSoup4, lxml

Base de Datos: PostgreSQL 15 (Docker Image), SQLAlchemy (ORM), psycopg2-binary

Integraciones: Telegram Bot API, python-dotenv

Nota sobre Mantenimiento (Disclaimer)
Importante: Este proyecto fue construido y probado con éxito en 2026. Las plataformas digitales (especialmente LinkedIn) actualizan frecuentemente sus estructuras de HTML, selectores CSS y políticas anti-scraping. Si en el futuro el script reporta 0 resultados en la extracción, la arquitectura del software (Base de datos en Docker, Filtros y Notificaciones) continuará intacta; solo se requerirá actualizar los selectores CSS dentro del módulo extractor de la plataforma afectada.

Requisitos Previos
Ya no es necesario instalar Python ni PostgreSQL en tu máquina local. Solo necesitas:

Escritorio Dockerinstalado y en ejecución.

Una cuenta de Telegram (Token de un Bot creado con BotFather y tu Chat ID).

Git para clonar el repositorio.

Instalación y Despliegue
1. Clonar el repositorio:

Intento
git clone https://github.com/tu-usuario/nombre-del-repo.git
cd nombre-del-repo
2. Configurar Variables de Entorno:
Crea un archivo llamado .env en la raíz del proyecto (al mismo nivel que docker-compose.yml) y configura tus credenciales. Asegúrate de no usar comillas en los valores:

Esto, TOML
# Configuración de PostgreSQL (Debe coincidir con docker-compose.yml)
POSTGRES_USER=tu_usuario
POSTGRES_PASSWORD=tu_contraseña
POSTGRES_DB=tu_base_de_datos
DB_HOST=postgres_db
DB_PORT=5432

# Credenciales de Telegram
TELEGRAM_BOT_TOKEN=tu_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui
3. Primera Ejecución (Construcción de la Imagen):
La primera vez tomará unos minutos mientras Docker descarga el navegador emulado y las librerías. Abre tu terminal en la carpeta del proyecto y ejecuta:

Intento
docker compose up --build
Verás en la consola cómo la base de datos se inicializa y luego el scraper comienza a buscar vacantes. Cuando termine, el contenedor del scraper mostrará exited with code 0 y recibirás los mensajes en tu Telegram.

Ejecuciones Posteriores
Una vez construida la imagen, ejecutar el scraper diariamente es instantáneo. Tienes dos opciones:

Opción A (Mediante Docker Desktop):

Escritorio Docker Abre.

Ve a la pestaña Containers.

Despliega el grupo de tu proyecto.

Presiona el botón de Play (Start) junto al contenedor python_scraper.

Opción B (Mediante Terminal):
Simplemente ejecuta el comando sin la bandera de construcción:

Intento
docker compose up
