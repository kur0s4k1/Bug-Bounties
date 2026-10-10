# [Título del hallazgo]

> Plantilla de writeup. Copia esta carpeta a `Findings/<Empresa>/<slug>/README.md`
> y completa cada sección. Elimina las notas entre corchetes.

| Campo | Valor |
|:--|:--|
| **Empresa / Target** | [p. ej. CODE.ORG] |
| **Programa** | [Bugcrowd / HackerOne / VDP Directo] |
| **Tipo** | [Web App / Source Code / ...] |
| **Clase de vulnerabilidad** | [IDOR / RCE / Broken Access Control / ...] |
| **Prioridad** | [P1–P5] |
| **Estado** | [Aceptado / Duplicado / No Aplica / En análisis] |
| **Fecha de hallazgo** | [DD/MM/AAAA] |
| **Recompensa** | [USD / Reconocimiento / —] |
| **CVE** | [CVE-XXXX-XXXXX, si aplica] |

---

## Resumen

[Descripción de dos o tres frases: qué es la vulnerabilidad, dónde estaba y cuál
fue el impacto. Sin jerga innecesaria.]

## Impacto

[Qué puede lograr un atacante con esto: confidencialidad, integridad,
disponibilidad. Cuantifica el alcance real observado (no teórico).]

## Contexto / Reconocimiento

[Cómo diste con el objetivo: qué activos, cómo los enumeraste, qué pistas
llevaron al endpoint o al código afectado.]

## Causa raíz

[Por qué existe la vulnerabilidad: ausencia de control de acceso, validación
insuficiente, lógica de negocio, etc. Evita afirmar la línea exacta de código
salvo que la hayas inspeccionado.]

## Reproducción

Pasos numerados y reproducibles. Incluye peticiones/respuestas **saneadas**
(host visible, rutas/parámetros/tokens enmascarados si la divulgación no está
autorizada).

1. ...
2. ...
3. ...

```http
GET /... HTTP/1.1
Host: [host]
...
```

**Evidencia:** [capturas, comparación baseline vs. exploit, logs]

## Prueba de concepto

[Código o comando mínimo, con placeholders para datos sensibles.]

## Divulgación responsable

- Reportado de forma privada a [programa] el [fecha].
- Resolución: [estado].
- Detalles completos publicados: [sí/no — y por qué].

## Remediación

[Qué debería corregir el equipo: control de autorización, validación, etc.]

## Referencias

- [Enlaces: aviso del programa, CVE, Hall of Fame, etc.]
