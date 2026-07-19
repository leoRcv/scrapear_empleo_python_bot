from database import SessionLocal, Vacante
from sqlalchemy import func

def verificar_totales():
    with SessionLocal() as session:
        # Cuenta cuántas vacantes hay en total
        total = session.query(func.count(Vacante.id)).scalar()
        print(f"Total de vacantes en la BD: {total}")
        
        # Muestra las últimas 5 vacantes de LinkedIn guardadas
        ultimas_linkedin = session.query(Vacante).filter(Vacante.portal == "LinkedIn").order_by(Vacante.id.desc()).limit(5).all()
        
        print("\nÚltimas 5 vacantes de LinkedIn:")
        for v in ultimas_linkedin:
            print(f"- {v.puesto} en {v.empresa}")
            print(f"  URL: {v.url}")

if __name__ == "__main__":
    verificar_totales()