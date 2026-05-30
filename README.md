#  Earth Risk Intelligence

Sistema de monitorización en tiempo real de terremotos y amenazas ambientales globales, con generación automática de alertas y visualización en mapa interactivo.

##  Arquitectura
##  Tecnologías

| Capa | Tecnología |
|---|---|
| Backend | Python, FastAPI |
| Base de datos | SQLite |
| Frontend | HTML, CSS, JavaScript |
| Mapa | Leaflet.js |
| Fuente de datos | USGS Earthquake API |
| Concurrencia | Python Threading |

##  Endpoints

| Endpoint | Descripción |
|---|---|
| `/earthquakes` | Datos de terremotos en tiempo real con coordenadas |
| `/alerts` | Alertas generadas automáticamente |
| `/health` | Estado del servicio |

## Cómo ejecutarlo en local

**1. Clona el repositorio**
```bash
git clone https://github.com/Argenika/earth-risk-dashboard.git
cd earth-risk-dashboard
```

**2. Instala las dependencias**
```bash
cd backend
pip install fastapi uvicorn requests
```

**3. Arranca el backend**
```bash
uvicorn main:app --reload
```

**4. Abre el frontend**

Abre `frontend/index.html` en el navegador.

##  Cómo funciona

1. Un worker en background consulta la API de USGS cada 60 segundos
2. Los datos se guardan en SQLite con coordenadas, magnitud y timestamp
3. Si la magnitud supera 4 → se genera una alerta automática con nivel de severidad
4. El frontend consulta la API cada 10 segundos y actualiza el mapa y las cards en tiempo real

##  Niveles de alerta

| Magnitud | Severidad |
|---|---|
| > 6 | 🔴 Alta |
| 4 - 6 | 🟡 Media |
