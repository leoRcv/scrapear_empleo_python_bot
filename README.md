# 🤖 Job Scraper & Telegram Notifier (Python Backend)

Un sistema automatizado de extracción de datos (Web Scraping) de grado de producción diseñado para monitorear ofertas de empleo orientadas al perfil Python, enfocado exclusivamente en mercados hispanohablantes (Paraguay, España, México, Argentina, Colombia y Chile). El sistema almacena las vacantes en una base de datos relacional para evitar duplicados y envía notificaciones en tiempo real mediante un bot de Telegram.

## 🚀 Arquitectura del Proyecto

Este proyecto está diseñado bajo una arquitectura modular y asíncrona:

1. **Extracción Inteligente (Scraping):** Combina `Playwright` para la emulación segura de navegación y `BeautifulSoup4` para el parseo del DOM. Implementa extracción basada en IDs únicos para blindar el sistema contra URLs dinámicas de rastreo.
2. **Filtrado Avanzado:** Cuenta con un motor de validación semántica que descarta automáticamente puestos enfocados a perfiles corporativos exclusivamente *Senior/Lead* o que exijan de forma explícita *inglés avanzado*, optimizando la calidad de las alertas para el usuario.
3. **Almacenamiento (Persistencia):** Conectado a `PostgreSQL` mediante un ORM (`SQLAlchemy`). Utiliza la instrucción de inserción segura `ON CONFLICT DO NOTHING` basada en restricciones de clave única (`UNIQUE`).
4. **Notificaciones (API):** Conexión nativa con la API de Telegram. Agrupa los mensajes en lotes (*batching*) para respetar los límites de la plataforma (*rate limits*).

## 🛠️ Tecnologías Utilizadas (Tech Stack)

- **Lenguaje:** Python 3.10+ (Programación Asíncrona / Asyncio)
- **Web Scraping:** Playwright, BeautifulSoup4, lxml
- **Base de Datos:** PostgreSQL, SQLAlchemy (ORM), psycopg2-binary
- **Integraciones:** Telegram Bot API, python-dotenv

## ⚠️ Nota sobre Mantenimiento (Disclaimer)

> **Importante:** Este proyecto fue construido y probado con éxito en 2026. Las plataformas digitales (especialmente LinkedIn) actualizan frecuentemente sus estructuras de HTML, selectores CSS y políticas anti-scraping. Si en el futuro el script reporta `0 resultados` en la extracción, la arquitectura del software (Base de datos, Filtros y Notificaciones) continuará intacta; solo se requerirá actualizar los selectores CSS dentro del módulo extractor de la plataforma afectada.

## ⚙️ Requisitos Previos

- Python 3 instalado.
- Servidor PostgreSQL activo localmente.
- Token de Bot de Telegram y Chat ID.

## 💻 Instalación y Uso Local

**1. Clonar el repositorio:**
```bash
git clone [https://github.com/tu-usuario/nombre-del-repo.git](https://github.com/tu-usuario/nombre-del-repo.git)
cd nombre-del-repo