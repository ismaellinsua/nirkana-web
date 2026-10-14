# Traspaso de la web a `nirkana-web` y repositorio antiguo en privado

**Estado (14/10/2026): este repositorio está listo. Falta que tú hagas los clics de GitHub, cuando quieras.**
`nirkana.es` sigue saliendo del repositorio antiguo (`smart-financial-advisor-demo`) hasta el paso 3. Nada de esto toca el DNS.

Mientras no se haga el traspaso, **cada cambio de la web se hace en los dos repositorios** (en el antiguo, con su petición de
cambios; aquí, directo) y `docs/` queda idéntico. Después del traspaso, solo aquí.

## Antes de empezar (lo comprobamos juntos; son 5 minutos)

1. **Que `docs/` de aquí es idéntico a lo publicado.** Se comprueba comparando con el repositorio antiguo (lo hace Claude: solo
   puede diferir en las 5 notas internas, que aquí viven en `notas/` y en el antiguo estaban en `docs/`).
2. **Pruebas en verde** aquí (Actions → Tests, Web) y el comprobador diario de la web sin avisos.
3. **¿Hay alguna app de Streamlit Cloud publicada desde el repositorio antiguo?** La web no la usa; si existe, dejará de
   funcionar al hacerlo privado. Mira en <https://share.streamlit.io>.
4. **Elige un momento tranquilo.** nirkana.es puede dar «404» entre 2 y 10 minutos, y el candado HTTPS nuevo puede tardar hasta
   una hora en estar listo (mientras tanto, el navegador puede avisar de certificado no válido).

## Los pasos (clics)

1. **`nirkana-web` → Settings → Pages.** *Build and deployment* → *Deploy from a branch* → rama `main` → carpeta **`/docs`** →
   **Save**. **No pongas el dominio todavía.** La web sale en `https://ismaellinsua.github.io/nirkana-web/` (sin estilos: usa
   rutas desde la raíz; es normal). En Actions debe aparecer «pages build and deployment» en verde.
2. **Repositorio antiguo → Settings → Pages.** Borra el *Custom domain* (`nirkana.es`) y guarda. **Haz el 3 justo después.**
3. **`nirkana-web` → Settings → Pages.** *Custom domain* → `nirkana.es` → **Save**. Espera al tic verde de la comprobación de DNS
   (no cambies nada en tu registrador). Cuando se pueda, marca **Enforce HTTPS**.
4. **Avisa a Claude.** Él lanza, desde la red de GitHub:
   - Actions → **Web** → *Run workflow* con **tras_traspaso** marcado: comprueba DNS, certificado, redirecciones, todas las
     páginas **y que las notas internas ya devuelven 404**.
   - Actions → **Probar la prueba como un visitante**: mide lo que vive quien pulsa «Probar gratis» en nirkana.es.

## Solo si el paso 4 sale bien: el repositorio antiguo, privado

> **No lo hagas privado antes de verificar.** GitHub Pages en un repositorio privado es de pago: una vez privado, el antiguo ya
> no podría volver a servir la web. Mientras sea público, volver atrás es poner de nuevo el dominio en su *Settings → Pages*.

5. **Repositorio antiguo → Settings → Actions → General → Disable actions.** Tiene flujos programados viejos (la copia de seguridad
   falla cada madrugada, avisos, disponibilidad): en privado gastarían minutos y mandarían correos de error.
6. **Quita la integración de Cloudflare** (*Workers Builds*, el aviso en rojo de las peticiones): GitHub → tu foto → *Settings* →
   *Applications* → *Installed GitHub Apps* → Cloudflare Workers and Pages → *Configure* → quita el acceso a ese repositorio (o
   desinstálala si no la usas).
7. **Repositorio antiguo → Settings → General → Danger Zone → Change visibility → Make private.**
8. *(Opcional)* Después, *Settings → General → Archive this repository*: queda de solo lectura.

## Después, en la cuenta y en este repositorio

- **Tu cuenta → Settings → Emails:** marca *Keep my email addresses private* y *Block command line pushes that expose my email*.
- **`nirkana-web` → Settings → Rules → Rulesets → Import a ruleset:** sube `ops/github/ruleset-main.json` (main protegida: sin
  borrar, sin reescribir historial, con petición de cambios y la prueba `tests` obligatoria).
- **`nirkana-web` → Settings → Code security:** activa *Secret Protection* (y *Push protection*) y las alertas de Dependabot.
- Claude cambia `web.yml` para que el comprobador diario use siempre `--sin-notas-internas` y actualiza los documentos de
  `nirkana-app` que citan el repositorio antiguo.

## Qué cambia en el día a día

- La web se edita aquí (`docs/`). La demo publicada es `docs/demo/index.html` (se genera en `nirkana-app`: `demo/LEEME.md`).
- `python ops/precio.py` lee o cambia el precio de la home en sus 8 sitios (`python ops/precio.py 60`).
- `python ops/legal.py` genera el aviso legal cuando haya datos (`legal/PENDIENTES-PUBLICACION.md`).
- Esta carpeta `notas/` es visible en GitHub (el repositorio es público) pero **no** se publica en nirkana.es.
