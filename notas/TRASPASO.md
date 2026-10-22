# Separar lo público de lo privado: la web a `nirkana-sitio` y todo lo demás en privado

**Estado (22/10/2026): Claude ha dejado preparado todo lo que no son clics de GitHub. Falta que tú crees un repositorio vacío y
hagas los clics de los pasos B, D y E, cuando quieras.** `nirkana.es` sigue saliendo del repositorio antiguo hasta el paso D3.
Nada de esto toca el DNS.

## La idea, en una frase

**Público: solo una copia de lo que ya ve cualquiera en nirkana.es** (`nirkana-sitio`). **Privado: todo lo demás** (el trabajo de la web,
las notas, el código de apoyo, las pruebas, la app, el producto anterior).

| Repositorio | Antes | Después | Qué lleva |
|---|---|---|---|
| `nirkana-sitio` (**nuevo**) | no existe | **público** | Solo `docs/` (las páginas, estilos, scripts e imágenes de la web), un README corto, una licencia de «todos los derechos reservados» (la de aquí nombra las librerías de la app anterior; la pública no) y el flujo que mantiene despierta la prueba. Historial nuevo y limpio: sin notas, sin código de apoyo, sin tu correo. |
| `nirkana-web` (este) | público | **privado** | El trabajo de la web: `docs/` (de aquí sale lo que se publica), `ops/`, `tests/`, `notas/`, `legal/`. |
| `smart-financial-advisor-demo` (el antiguo) | público, sirve nirkana.es | **privado** (y archivado) | El producto anterior (Streamlit), `marketing/`, `ops/` viejo. Con él se queda todo su historial, que deja de verse. |
| `nirkana-app` | privado | privado | La aplicación. |

**Cómo se publica a partir de ahora:** el cambio se hace aquí (en privado), pasa las pruebas y `python ops/publicar_sitio.py
../nirkana-sitio` copia a la copia pública **solo** lo permitido (páginas, estilos, scripts, imágenes, la hoja de Excel,
`robots.txt` y `sitemap.xml`). Si algo que no es de la web se cuela en `docs/` (una nota, un `.py`, un `.json`…), el script se
detiene y `tests/web-publico.test.mjs` falla. Después se confirma y se sube en `nirkana-sitio`.

## Lo que ya está hecho (no hay que tocar nada)

- Las cuatro notas internas que se publicaban en `nirkana.es/<nombre>.md` están fuera de `docs/` (en el repositorio antiguo, PR #79).
- `ops/publicar_sitio.py` y sus pruebas; `ops/publico/` (README y flujo de la copia pública); `/caja/` (el mini-programa de caja de la
  versión anterior, sin enlazar) quitado del sitio.
- El flujo «Despertar la prueba» está preparado para la copia pública (`ops/publico/despertar-prueba.yml`): allí los minutos de
  Actions son gratis; en un repositorio privado se acabarían en pocos días. **Hasta el traspaso sigue corriendo aquí**
  (`.github/workflows/despertar-prueba.yml`, este repositorio aún es público) para que la prueba no se duerma; en el paso D4 Claude
  lo borra de aquí cuando comprueba que ya corre en `nirkana-sitio`.

## Los pasos que haces tú (clics)

### A. Tu correo, fuera de los commits (1 minuto, antes de B)

Tu foto → **Settings → Emails** → marca **Keep my email addresses private** y **Block command line pushes that expose my email**.
Así, el commit que GitHub hace por ti al poner el dominio (paso D3) no lleva tu correo personal.

### B. Crear el repositorio público vacío (2 minutos)

1. <https://github.com/new> → *Owner* `ismaellinsua` → *Repository name* **`nirkana-sitio`** → **Public** → **sin** README, **sin**
   .gitignore, **sin** licencia → **Create repository**.
2. Si la app de Claude en GitHub está instalada solo en repositorios elegidos: tu foto → **Settings → Applications → Installed
   GitHub Apps → Claude → Configure → Repository access** → añade `nirkana-sitio` (si está en *All repositories*, no hace falta).
3. **Avisa a Claude.** Él sube el contenido (un primer commit con la web tal como está publicada hoy, sin notas ni `/caja/`) y
   comprueba que es idéntico.

### C. Antes de seguir (lo comprobamos juntos; son 5 minutos)

1. Que el contenido de `nirkana-sitio` es idéntico a lo publicado (lo hace Claude).
2. **¿Hay alguna app de Streamlit Cloud publicada desde el repositorio antiguo?** La web no la usa; si existe, dejará de funcionar
   al hacerlo privado. Mira en <https://share.streamlit.io>.
3. **Elige un momento tranquilo.** nirkana.es puede dar «404» entre 2 y 10 minutos, y el candado HTTPS nuevo puede tardar hasta una
   hora (mientras tanto, el navegador puede avisar de certificado no válido).

### D. El traspaso del dominio

1. **`nirkana-sitio` → Settings → Pages.** *Build and deployment* → *Deploy from a branch* → rama `main` → carpeta **`/docs`** →
   **Save**. **No pongas el dominio todavía.** La web sale en `https://ismaellinsua.github.io/nirkana-sitio/` (sin estilos: usa rutas
   desde la raíz; es normal). En Actions debe aparecer «pages build and deployment» en verde.
2. **Repositorio antiguo → Settings → Pages.** Borra el *Custom domain* (`nirkana.es`) y guarda. **Haz el 3 justo después.**
3. **`nirkana-sitio` → Settings → Pages.** *Custom domain* → `nirkana.es` → **Save**. Espera al tic verde de la comprobación de DNS
   (no cambies nada en tu registrador). Cuando se pueda, marca **Enforce HTTPS**.
4. **Avisa a Claude.** Él lo comprueba desde la red de GitHub: DNS, certificado, redirecciones, todas las páginas, que las notas
   internas dan 404 y que la prueba de 24 horas responde (Actions → **Web** → *Run workflow* con **tras_traspaso** marcado, y
   «Probar la prueba como un visitante»). También lanza «Despertar la prueba» a mano en `nirkana-sitio` y, si responde, lo
   borra de este repositorio (dos avisos a la vez no hacen daño, pero uno sobra).

### E. Solo si D4 sale bien: todo lo demás, en privado

> **No lo hagas antes de verificar.** GitHub Pages en un repositorio privado es de pago: una vez privado, el antiguo ya no podría
> volver a servir la web. Mientras sea público, volver atrás es poner de nuevo el dominio en su *Settings → Pages*.

5. **Repositorio antiguo → Settings → Actions → General → Disable actions.** Tiene flujos programados viejos (la copia de seguridad
   falla cada madrugada, avisos, disponibilidad): en privado gastarían minutos y mandarían correos de error.
6. **Quita la integración de Cloudflare** del repositorio antiguo (*Workers Builds*, el aviso de las peticiones de cambios): tu foto →
   *Settings* → *Applications* → *Installed GitHub Apps* → Cloudflare Workers and Pages → *Configure* → quita el acceso a ese
   repositorio. **Mira antes si publica algo en una dirección `*.workers.dev`:** ese contenido seguiría siendo público.
7. **Repositorio antiguo → Settings → General → Danger Zone → Change visibility → Make private.** *(Opcional)* después, *Archive this
   repository*.
8. **`nirkana-web` (este) → Settings → Pages → Build and deployment → *Branch*: **None** → Save** (hoy también publica la web en
   `ismaellinsua.github.io/nirkana-web`, sin dominio; al hacerlo privado dejaría de verse igualmente, pero así queda dicho).
   Después: **Settings → General → Danger Zone → Change visibility → Make private.** Antes de estos clics, Claude confirma
   que este repositorio ya no sirve nada y que «Despertar la prueba» ya no corre aquí sino en `nirkana-sitio` (en privado, un aviso
   cada 5 minutos gastaría los minutos gratuitos del mes en pocos días).

### F. Después

- **`nirkana-sitio` → Settings → Code security:** activa *Secret Protection* (y *Push protection*). Es el único repositorio público:
  que nunca se pueda subir ahí una clave por error.
- **`nirkana-sitio` → Settings → Rules → Rulesets → New ruleset → New branch ruleset** *(opcional)*: nombre `main`, *Enforcement
  status* **Active**, *Target branches* → *Add target* → **Include default branch**, y marca solo **Restrict deletions** y **Block
  force pushes**. Así `main` no se puede borrar ni reescribir. **No** marques «Require a pull request» ni «Require status checks»:
  ahí no hay pruebas (viven en privado) y te bloquearían a ti y a Claude. *(No subas `ops/github/ruleset-main.json`: es el de este
  repositorio y exige la comprobación «tests».)*
- **Verifica el dominio** *(opcional, recomendado)*: tu foto → **Settings → Pages → Add a domain** → `nirkana.es` → GitHub te da un
  registro TXT que añades en tu registrador (no cambia nada de la web) → **Verify**. Así ninguna otra cuenta de GitHub puede publicar
  una web en `nirkana.es`, ni siquiera en los minutos en que el dominio no esté puesto en ningún repositorio.
- Los avisos automáticos (comprobación diaria de la web, pruebas) pasan a gastar minutos de Actions de repositorios **privados**
  (2.000 al mes gratis, para todos tus repositorios privados juntos). Si se acaban, esos avisos dejan de salir hasta el mes siguiente;
  un monitor externo gratuito (UptimeRobot, 5 minutos de intervalo) vigila la web y la prueba sin gastar minutos.
- Claude actualiza los documentos de `nirkana-app` que citan el repositorio antiguo.

## Qué cambia en el día a día

- La web se edita aquí (`docs/`), en privado. Se publica con `python ops/publicar_sitio.py ../nirkana-sitio` y un commit allí.
- La demo publicada es `docs/demo/index.html` (se genera en `nirkana-app`: `demo/LEEME.md`). **Es código que cualquiera puede ver en
  nirkana.es:** lo que se publica en una web siempre se puede leer, así que la demo solo debe llevar datos y lógica ficticios.
- `python ops/precio.py` lee o cambia el precio de la home en sus 8 sitios (`python ops/precio.py 60`).
- `python ops/legal.py` genera el aviso legal cuando haya datos (`legal/PENDIENTES-PUBLICACION.md`).
- Esta carpeta `notas/` es privada en cuanto este repositorio lo sea; mientras tanto, **no se publica** en nirkana.es ni en `nirkana-sitio`.
