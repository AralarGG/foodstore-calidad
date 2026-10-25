# Food Store: automatización de calidad

Catálogo, cobro, envío y reportes de ventas del Food Store (Python), con
controles de calidad automáticos antes de cada commit.

Los reportes por canal (`reporte_mostrador.py` y `reporte_online.py`) delegan
en `reporte_ventas.py`, que concentra la regla de monto neto por medio de pago.

## Requisitos

Python 3.10 o superior y Git.

```
py -m pip install -r requirements-dev.txt
py -m pre_commit install
```

(En Linux o macOS, reemplazar `py` por `python3`.)

- `requirements.txt`: dependencias de producción (auditadas con pip-audit).
- `requirements-dev.txt`: herramientas de pruebas y análisis.

## Pre-commit hook

Configurado en `.pre-commit-config.yaml`. Antes de cada commit corre, en orden,
Black (formatter), Flake8 (linter, con límite de complejidad 10) y la suite de
pytest. Si uno falla, el commit se aborta.

Para correrlo sobre todo el repositorio sin hacer commit:

```
py -m pre_commit run --all-files
```

## Análisis estático

```
py -m radon cc src -s -a
py -m pylint --disable=all --enable=duplicate-code src
py -m pip_audit -r requirements.txt
```

## Cobertura

```
py -m pytest --cov=src --cov-branch --cov-report=term-missing --cov-fail-under=80
```

## Estructura

```
foodstore-calidad/
    .github/
        ISSUE_TEMPLATE/
            bug_report.md
            deuda_tecnica.md
        pull_request_template.md
    src/
        catalogo.py
        envio.py
        reporte_mostrador.py
        reporte_online.py
        reporte_ventas.py
        servicio_cobro.py
    tests/
        test_catalogo.py
        test_costo_envio.py
        test_precio_combo.py
        test_reportes.py
        test_servicio_cobro.py
    .flake8
    .gitignore
    .pre-commit-config.yaml
    pytest.ini
    requirements.txt
    requirements-dev.txt
    README.md
```
