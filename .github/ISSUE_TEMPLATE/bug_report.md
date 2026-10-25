---
name: Reporte de defecto
about: Plantilla obligatoria para reportar un fallo funcional o lógico del sistema
title: "BUG: [resumen breve del fallo]"
labels: ["bug", "dod-pendiente"]
assignees: ''
---

## Descripción técnica del problema
<!-- Explicar qué falla, en qué módulo o endpoint y bajo qué condiciones. Evitar frases como "no anda" o "tira error". -->

**Módulo / endpoint afectado:**
**Severidad:** <!-- Crítica / Alta / Media / Baja -->

## Entorno de ejecución
- Rama o commit: 
- Sistema operativo: 
- Versión de Python: 
- Base de datos / dependencias relevantes: 

## Pasos para reproducir
<!-- Lista numerada y determinista. Siguiendo estos pasos el fallo tiene que ocurrir siempre. Incluir los datos de entrada exactos. -->
1. 
2. 
3. 

**Frecuencia:** <!-- Siempre / Intermitente (indicar cada cuántos intentos) -->

## Comportamiento esperado
<!-- Qué debería hacer el sistema según la especificación, el contrato de la API o el criterio de aceptación de la historia. -->

## Comportamiento observado
<!-- Qué hace realmente: mensaje de error, código HTTP recibido, dato incorrecto, congelamiento, etc. -->

## Evidencias adjuntas
<!-- Marcar lo que se adjunta. Un reporte sin evidencia no se toma para trabajar. -->
- [ ] Captura de pantalla
- [ ] Log de consola o stack trace
- [ ] Request / response de la API
- [ ] Reporte de la corrida de tests

```
Pegar acá el log o el stack trace
```

## Checklist del reportante
- [ ] Verifiqué que no existe otro issue abierto con el mismo problema
- [ ] Los pasos permiten reproducir el fallo en otra máquina
- [ ] Adjunté al menos una evidencia
