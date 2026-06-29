# ISO Smart MedSupplier Frontend

Frontend React/Vite propio de MedSupplier.

## Entorno local reproducible

```bash
cd /home/felipe/proyectos/ISO_Smart_MedSupplier/frontend
npm ci
```

Para desarrollo local:

```bash
npm run dev -- --host 127.0.0.1 --port 3001
```

## Contrato de validacion

```bash
cd /home/felipe/proyectos/ISO_Smart_MedSupplier/frontend
npm run lint
npm run build
npm run test:e2e:medsupplier
```

El E2E de MedSupplier levanta el backend desde `../backend` usando `../backend/.venv312/bin/python` por defecto. No debe apuntar al venv de ISO Smart.

## Configuracion runtime

Variables utiles:

```bash
BASE_URL=http://127.0.0.1:3001
VITE_API_PROXY_TARGET=http://127.0.0.1:18002
VITE_LOCAL_AUTH_BYPASS=1
PYTHON_BIN=/home/felipe/proyectos/ISO_Smart_MedSupplier/backend/.venv312/bin/python
```

`PYTHON_BIN` es opcional; si se define, debe apuntar a un interprete del backend de MedSupplier.
