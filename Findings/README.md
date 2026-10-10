# Findings — Writeups detallados

Cada hallazgo con **divulgación autorizada** o **ya resuelto** puede tener su
writeup técnico completo en una subcarpeta:

```
Findings/
├── TEMPLATE/                 # Plantilla base
├── <Empresa>/
│   └── <slug-del-hallazgo>/
│       ├── README.md         # Writeup (ver TEMPLATE/README.md)
│       └── img/              # Capturas saneadas
└── README.md                 # Este archivo
```

## Reglas de contenido

- **Sanea** rutas, parámetros, tokens y payloads mientras la divulgación no esté
  autorizada. Conserva el host como prueba de alcance.
- **No publiques** PII de terceros, credenciales ni secretos activos.
- Marca cada writeup con su estado (**Aceptado / Duplicado / No Aplica / En
  análisis**) y su estado de divulgación.
- Usa nombres de carpeta en `slug-case` (minúsculas, guiones).

## Índice de writeups

> Aún no hay writeups detallados publicados. Los hallazgos resumidos viven en el
> [README principal](../README.md).

| Empresa | Hallazgo | Estado | Divulgación | Enlace |
|:--|:--|:--|:--|:--|
| — | — | — | — | — |

Para empezar uno nuevo:

```bash
mkdir -p "Findings/<Empresa>/<slug-del-hallazgo>/img"
cp Findings/TEMPLATE/README.md "Findings/<Empresa>/<slug-del-hallazgo>/README.md"
```
