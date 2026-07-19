import os
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Dict
from sqlalchemy import create_engine, String, DateTime, UniqueConstraint, inspect, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.dialects.postgresql import insert

# Carga las variables de entorno desde el archivo .env a la memoria
load_dotenv()

# CONFIGURACION DE TU CONEXION A POSTGRES
USUARIO = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PUERTO = os.getenv("DB_PORT")
BASE_DATOS = os.getenv("DB_NAME")

# URL de conexión estándar que requiere SQLAlchemy para comunicarse con el driver psycopg2
DATABASE_URL = f"postgresql+psycopg2://{USUARIO}:{PASSWORD}@{HOST}:{PUERTO}/{BASE_DATOS}"

# 1. Creamos el motor de la base de datos (Engine)
engine = create_engine(DATABASE_URL, echo=False)

# 2. Creamos la fábrica de sesiones para interactuar con la DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Definimos la Clase Base de la cual heredarán nuestros modelos
class Base(DeclarativeBase):
    pass

# 4. Definimos el Modelo (Nuestra tabla en Postgres expresada como clase Python)
class Vacante(Base):
    __tablename__ = "vacantes"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    portal: Mapped[str] = mapped_column(String(50), nullable=False)
    puesto: Mapped[str] = mapped_column(String(255), nullable=False)
    empresa: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


def asegurar_restriccion_unica_url():
    """
    Garantiza que la tabla existente tenga una restricción única sobre url.

    create_all() crea tablas nuevas, pero no añade restricciones a tablas ya existentes.
    """
    inspector = inspect(engine)

    if not inspector.has_table("vacantes"):
        return

    unique_constraints = inspector.get_unique_constraints("vacantes")
    nombres_existentes = {constraint["name"] for constraint in unique_constraints if constraint.get("name")}
    columnas_con_indice_unico = {
        tuple(indice["column_names"])
        for indice in inspector.get_indexes("vacantes")
        if indice.get("unique")
    }

    if "uq_vacantes_url" in nombres_existentes or ("url",) in columnas_con_indice_unico:
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE vacantes ADD CONSTRAINT uq_vacantes_url UNIQUE (url)"))


def inicializar_db():
    """
    Responsabilidad: Conectarse al servidor y crear la tabla reflejando 
    las propiedades definidas en nuestra clase Vacante.
    """
    print("[SQLAlchemy] Verificando y creando tablas de forma ORM...")
    try:
        # Esto lee todas las clases que heredan de Base y crea las tablas si no existen
        Base.metadata.create_all(bind=engine)
        asegurar_restriccion_unica_url()
        print("[SQLAlchemy] Tabla 'vacantes' lista para producción.")
    except Exception as e:
        print(f"[SQLAlchemy] Error al inicializar las tablas: {e}")


def guardar_empleos(empleos_datos: List[Dict[str, str]]) -> List[Dict[str, str]]:
    print(f"[SQLAlchemy] Procesando {len(empleos_datos)} vacantes para insertar...")
    
    # Aquí guardaremos solo las ofertas que son realmente nuevas
    empleos_nuevos = []
    
    with SessionLocal() as session:
        try:
            for datos in empleos_datos:
                stmt = insert(Vacante).values(
                    portal=datos["portal"],
                    puesto=datos["puesto"],
                    empresa=datos["empresa"],
                    url=datos["url"]
                ).on_conflict_do_nothing(index_elements=["url"])
                
                resultado = session.execute(stmt)
                
                if resultado.rowcount > 0:
                    empleos_nuevos.append(datos)
            
            session.commit()
            print(f"[SQLAlchemy] Guardado completado. Se añadieron {len(empleos_nuevos)} nuevas ofertas.")
            
        except Exception as e:
            session.rollback()
            print(f"[SQLAlchemy] Error durante la inserción masiva: {e}")
            
    return empleos_nuevos