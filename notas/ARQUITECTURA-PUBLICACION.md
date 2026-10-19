# NirKanA: límites entre web, demostración, prueba y producto comercial

*Al día el 19 de octubre de 2026. Sustituye al texto del 10-14 de octubre, que hablaba de repositorios privados, de Cloudflare y de una prueba
todavía sin desplegar.*

## Qué es cada cosa
- `nirkana-app` (repositorio **privado**): la aplicación comercial (FastAPI y PWA). En modo `produccion` es la de los clientes de pago: el
  servicio `nirkana` de Render existe pero **todavía no está desplegado**; su dirección prevista es `app.nirkana.es`.
- El mismo código en modo `prueba`, con **otra base de datos** (Neon propia), es la prueba de 24 horas: servicio `nirkana-prueba` de Render, en
  `https://nirkana-prueba.onrender.com` (sin dominio propio por ahora). `TRIAL_URL` de `docs/assets/site.js` apunta a ella.
- `docs/` de este repositorio (**público**): la web comercial estática de `nirkana.es`, publicada con GitHub Pages. Hoy sigue saliendo del
  repositorio antiguo; pasará a salir de este con el traspaso (`TRASPASO.md`).
- `docs/demo/`: la demostración **sin registro**, con datos ficticios, que funciona dentro del navegador. No es la prueba de 24 horas.
- El producto anterior (Streamlit, `sales_manager/`) sigue en el repositorio antiguo, que pasará a privado. No debe convertirse en backend de
  clientes ni conectarse a datos de producción.

## Reglas antes de publicar
1. No activar un enlace a un servicio hasta verificar HTTPS, despliegue, salud de la base de datos y separación de credenciales. Con la prueba
   se hizo así (`comprobar-despliegue` de `nirkana-app` y «Probar la prueba como un visitante» de este repositorio) y
   `tests/web-boundaries.test.mjs` solo admite esa dirección.
2. No copiar secretos ni datos de clientes a GitHub Pages ni a `docs/demo/`.
3. `APP_URL` sigue vacío hasta que exista la app de clientes. `TRIAL_URL` ya está puesto. `DEMO_URL` es `/demo/`.
4. La demostración sin registro no promete 24 horas de acceso; ese plazo es solo del servicio en modo `prueba`.
5. Toda venta o contratación real se gestiona desde `nirkana.oficial@gmail.com` hasta validar el circuito de pagos.
6. Los repositorios de la web (este y el antiguo) son públicos: nada que no deba verse puede estar en ellos.
7. No afirmar conformidad fiscal o VERI*FACTU sin pruebas oficiales y revisión legal (`tests/web-claims.test.mjs` lo impide).
8. Antes de fusionar un cambio: pasar las pruebas, revisar los enlaces y mirar la web en móvil y en escritorio.

## Flujo comercial
Visita a `nirkana.es` → demostración inmediata (opcional) → prueba de 24 horas (activa) → contacto, con el 20 % de descuento en la instalación
→ alta manual del cliente en producción.

## Riesgo pendiente
Mientras el repositorio antiguo siga siendo público, contiene además `sales_manager/`, `ops/`, `legal/` y `marketing/`, y publica en
`nirkana.es` cuatro notas internas que aquí viven en `notas/`. Por eso la web se traspasa a este repositorio y el antiguo pasa a privado
(`TRASPASO.md`).
