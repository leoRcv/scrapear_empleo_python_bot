import asyncio
import re
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from database import inicializar_db, guardar_empleos
from notifications import enviar_notificacion

async def obtener_html(url: str) -> str:
    """Abre el navegador y descarga el HTML en bruto."""
    print(f"[Playwright] Navegando hacia: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await page.set_viewport_size({"width": 1280, "height": 800})
        
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(4000) 
        
        html_puro = await page.content()
        await browser.close()
        return html_puro

# ==========================================
# FILTROS Y MODULOS DE EXTRACCION
# ==========================================

def es_vacante_valida_linkedin(puesto: str) -> bool:
    """Retorna False si el título sugiere inglés avanzado o seniority alto."""
    puesto_min = puesto.lower()
    
    # Lista de palabras clave que queremos esquivar
    palabras_prohibidas = [
        "senior", "sr", "lead", "principal", "english required", 
        "advanced english", "b2", "c1", "c2", "fluent", "inglés avanzado"
    ]
    
    for palabra in palabras_prohibidas:
        if palabra in puesto_min:
            return False
    return True


def extraer_remoteok(html_content: str) -> list:
    """Extrae empleos de RemoteOK"""
    print("[BeautifulSoup] Extrayendo datos de RemoteOK...")
    soup = BeautifulSoup(html_content, "lxml")
    lista_empleos = []
    
    tarjetas = soup.select("tr.job, tr[data-href*='/remote-jobs/'], tr[data-url*='/remote-jobs/']")
    for tarjeta in tarjetas:
        tag_titulo = tarjeta.find("h2") or tarjeta.find("h3") or tarjeta.find("h1")
        tag_empresa = tarjeta.find("h3", itemprop="name") or tarjeta.find("div", class_="company")
        
        # Obtenemos la ruta relativa desde los atributos de la fila
        ruta_relativa = tarjeta.get("data-href") or tarjeta.get("data-url")
        
        # Si no existía, la buscamos dentro del enlace tradicional
        if not ruta_relativa:
            tag_enlace = tarjeta.find("a", itemprop="url")
            ruta_relativa = tag_enlace.get("href") if tag_enlace else None

        if tag_titulo and ruta_relativa:
            puesto = tag_titulo.text.strip()
            empresa = tag_empresa.text.strip() if tag_empresa else "Empresa Confidencial"
            
            # Limpiamos los parámetros de la URL de RemoteOK
            ruta_limpia = ruta_relativa.split('?')[0]
            url_absoluta = f"https://remoteok.com{ruta_limpia}" if ruta_limpia.startswith("/") else ruta_limpia

            lista_empleos.append({
                "portal": "RemoteOK",
                "puesto": puesto,
                "empresa": empresa,
                "url": url_absoluta
            })
    return lista_empleos


def extraer_linkedin(html_content: str) -> list:
    print("[BeautifulSoup] Extrayendo datos de LinkedIn (Hibrido + ID Unico + Filtro)...")
    soup = BeautifulSoup(html_content, "lxml")
    lista_empleos = []
    
    tarjetas_publicas = soup.find_all("div", class_="base-card")
    tarjetas_privadas = soup.find_all("div", class_=lambda c: c and "job-card-list__entity-lockup" in c)
    
    # Regex para capturar el ID numérico real del empleo de LinkedIn
    regex_id = re.compile(r"/view/(\d+)")

    # --- Procesar HTML Público ---
    for tarjeta in tarjetas_publicas:
        tag_titulo = tarjeta.find("h3", class_="base-search-card__title")
        tag_empresa = tarjeta.find("a", class_="hidden-nested-link") or tarjeta.find("h4", class_="base-search-card__subtitle")
        tag_enlace = tarjeta.find("a", class_="base-card__full-link")
        
        if tag_titulo and tag_enlace:
            puesto = tag_titulo.text.strip()
            
            # Aplicar filtro de idioma y seniority exclusivo para LinkedIn
            if not es_vacante_valida_linkedin(puesto):
                continue
                
            empresa_sucia = tag_empresa.text if tag_empresa else "Empresa Confidencial"
            url_sucia = tag_enlace.get("href") or ""
            
            match = regex_id.search(url_sucia)
            url_limpia = f"https://www.linkedin.com/jobs/view/{match.group(1)}" if match else url_sucia.split("?")[0].split("#")[0]

            lista_empleos.append({
                "portal": "LinkedIn",
                "puesto": puesto,
                "empresa": " ".join(empresa_sucia.split()),
                "url": url_limpia
            })

    # --- Procesar HTML Privado ---
    for tarjeta in tarjetas_privadas:
        tag_enlace = tarjeta.find("a", class_=lambda c: c and "job-card-list__title--link" in c)
        tag_empresa = tarjeta.find("div", class_=lambda c: c and "artdeco-entity-lockup__subtitle" in c)
        
        if tag_enlace:
            puesto = tag_enlace.get("aria-label") or tag_enlace.text.strip()
            puesto_limpio = puesto.replace("\n", "").strip()
            
            #Aplicar Filtro de Idioma y Seniority exclusivo para LinkedIn
            if not es_vacante_valida_linkedin(puesto_limpio):
                continue
                
            empresa_sucia = tag_empresa.text if tag_empresa else "Empresa Confidencial"
            ruta = tag_enlace.get("href") or ""
            
            match = regex_id.search(ruta)
            if match:
                url_limpia = f"https://www.linkedin.com/jobs/view/{match.group(1)}"
            else:
                url_limpia = f"https://www.linkedin.com{ruta.split('?')[0]}" if ruta.startswith("/") else ruta.split('?')[0]

            lista_empleos.append({
                "portal": "LinkedIn",
                "puesto": puesto_limpio,
                "empresa": " ".join(empresa_sucia.split()),
                "url": url_limpia
            })
            
    return lista_empleos


async def main():
    inicializar_db()
    todas_las_vacantes = []

    # --- 1. PROCESAR REMOTEOK ---
    url_remoteok = "https://remoteok.com/remote-python-jobs"
    html_remoteok = await obtener_html(url_remoteok)
    todas_las_vacantes.extend(extraer_remoteok(html_remoteok))
    
    # --- 2. PORTALES DE LINKEDIN POR pasi
    paises_busqueda = [
        {"nombre": "Paraguay", "url": "https://www.linkedin.com/jobs/search?keywords=Python&location=Paraguay"},
        {"nombre": "España", "url": "https://www.linkedin.com/jobs/search?keywords=Python&location=Spain"},
        {"nombre": "México", "url": "https://www.linkedin.com/jobs/search?keywords=Python&location=Mexico"},
        {"nombre": "Argentina", "url": "https://www.linkedin.com/jobs/search?keywords=Python&location=Argentina"},
        {"nombre": "Colombia", "url": "https://www.linkedin.com/jobs/search?keywords=Colombia"},
        {"nombre": "Chile", "url": "https://www.linkedin.com/jobs/search?keywords=Python&location=Chile"}
    ]

    for pais in paises_busqueda:
        print(f"Buscando activamente ofertas en LinkedIn: {pais['nombre']}...")
        html_linkedin = await obtener_html(pais["url"])
        todas_las_vacantes.extend(extraer_linkedin(html_linkedin))
    
    # --- 3. REPORTE Y GUARDADO ---
    print(f"\n[Resultado] Se recolectaron en total {len(todas_las_vacantes)} empleos estructurados.")
    
    if todas_las_vacantes:
        empleos_nuevos = guardar_empleos(todas_las_vacantes)
        if empleos_nuevos:
            enviar_notificacion(empleos_nuevos)
        else:
            print("Todos los empleos encontrados ya estaban en la base de datos.")
    else:
        print("No se encontraron empleos para procesar.")

if __name__ == "__main__":
    asyncio.run(main())