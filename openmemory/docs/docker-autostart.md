# Autostart de contenedores Docker 🐳

Este documento explica cómo asegurarte de que los contenedores de OpenMemory se inicien automáticamente cuando arranque Docker Desktop o el sistema.

## Cambios aplicados
- Añadido `restart: unless-stopped` a los servicios en `docker-compose.yml`:
  - `mem0_store` (qdrant)
  - `openmemory-mcp` (API)
  - `openmemory-ui` (UI)

## Pasos para verificar localmente ✅
1. Asegúrate de que Docker Desktop arranque al iniciar sesión en Windows:
   - Abre **Docker Desktop > Settings > General** y activa **Start Docker Desktop when you log in**.

2. Si ya tienes contenedores en ejecución y quieres aplicar la política de reinicio sin recrearlos:

```bash
# Reemplaza <container> por el nombre o id del contenedor
docker update --restart unless-stopped <container>
```

3. Para (re)crear los servicios con la configuración nueva:

```bash
# En la carpeta del proyecto
docker compose down
docker compose up -d
```

4. Verificar la política de reinicio en un contenedor:

```bash
docker inspect --format '{{.HostConfig.RestartPolicy.Name}}' <container>
# Resultado esperado: unless-stopped
```

5. Prueba final: reinicia Docker Desktop o reinicia Windows y confirma que los contenedores vuelven a aparecer y están en estado "running".
