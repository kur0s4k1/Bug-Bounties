# Política de Divulgación Responsable

Este repositorio es un **portafolio de investigación de vulnerabilidades**. Todo el
trabajo aquí documentado se realizó dentro del alcance y las reglas de programas de
bug bounty (Bugcrowd, HackerOne) o programas de divulgación de vulnerabilidades
(VDP) de las organizaciones afectadas, y de forma directa cuando la organización
lo autorizó.

## Principios

1. **Alcance autorizado.** Ninguna prueba se ejecuta fuera del scope definido por
   el programa. No se accede a datos que excedan lo mínimo necesario para
   demostrar el impacto (prueba de concepto).
2. **Minimización de daño.** Se evita cualquier acción destructiva, degradación de
   servicio, acceso persistente o exfiltración masiva de información.
3. **Reporte privado primero.** Todos los hallazgos se reportaron de forma privada
   a la organización a través de su canal oficial antes de cualquier publicación.
4. **Coordinación de divulgación.** Los detalles técnicos completos se publican
   únicamente cuando la organización ha resuelto el reporte y/o autorizado la
   divulgación pública.
5. **Saneado por defecto.** Mientras la divulgación no esté autorizada, los
   endpoints, rutas, parámetros, payloads, tokens y datos personales se muestran
   **enmascarados** (se conserva el host como evidencia de alcance y se oculta el
   resto).

## Manejo de datos sensibles

- **PII / datos de terceros:** nunca se publican. Cualquier dato personal
  observado se redacta o elimina del repositorio.
- **Credenciales, tokens y secretos:** nunca se publican, ni siquiera parciales,
  salvo confirmación explícita de que ya fueron revocados y la organización
  autoriza su mención.
- **Endpoints explotables:** saneados por defecto. Ver la constante
  `SANITIZE_ASSET` en [`scripts/build_index.py`](scripts/build_index.py).

## Sobre las recompensas y estados

- **Aceptado:** el programa validó el hallazgo.
- **Duplicado:** hallazgo válido pero reportado previamente por otro investigador;
  se documenta como evidencia de metodología, no como descubrimiento original.
- **No Aplica:** el programa determinó que el hallazgo está fuera de los criterios
  o del scope de recompensa.
- **En análisis:** en proceso de triaje por parte del programa.

Las recompensas mostradas reflejan los montos públicos/otorgados por cada
programa.

## Contacto

Para coordinación de divulgación, correcciones o retiro de contenido, contacta vía
[GitHub](https://github.com/kur0s4k1).
