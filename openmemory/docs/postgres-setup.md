# Conectar OpenMemory a PostgreSQL (local o contenedor)

Este documento explica cómo volver a la configuración que usabas: conectar la API a una base de datos PostgreSQL en tu máquina local (`postgres` usuario, base de datos `openmemory`) o, si prefieres, arrancar un contenedor PostgreSQL.

## 1) Usar PostgreSQL local (recomendado si ya lo tienes)

- Verifica que `api/.env` tenga la URL correcta:

```env
DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/openmemory
```

- `host.docker.internal` permite que los contenedores Docker en Windows se conecten a servicios que se ejecutan en el host.

- Asegúrate de que la base de datos `openmemory` exista y que el usuario `postgres` tenga permiso:

```bash
# Desde tu máquina (psql debe estar instalado)
psql -U postgres -h localhost -c "CREATE DATABASE openmemory;"
# O con Docker (si prefieres)
docker run --rm -it postgres:16 psql -h host.docker.internal -U postgres -c "CREATE DATABASE openmemory;"
```

- Inicia los servicios sin requerir un contenedor `mem0_store`:

```bash
cd C:\mem0\openmemory
docker compose up -d
```

La API usará `DATABASE_URL` de `api/.env`. Hemos quitado la dependencia directa a `mem0_store` para que puedas usar tu Postgres local.

## 2) Usar PostgreSQL en un contenedor (opcional)

Si prefieres que la base de datos también esté en Docker, usamos el archivo `compose/pgvector.yml` que ya existe y define un servicio `mem0_store` con Postgres y pgvector.

```bash
# Levanta la base de datos junto con los servicios principales
docker compose -f docker-compose.yml -f compose/pgvector.yml up -d
```

El servicio `mem0_store` escuchará en el puerto 5432 dentro del host. Ajusta `api/.env` si quieres apuntarlo a `postgresql://mem0_store:5432/mem0`.

## 3) Verificación

- Revisa logs de la API:

```bash
docker compose logs -f openmemory-mcp
```

- Comprueba que la app se conectó a la base de datos (busca mensajes de conexión en los logs o errores de migración).

---
