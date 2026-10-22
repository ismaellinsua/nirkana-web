# nirkana.es (trabajo de la web)

Este repositorio es el **trabajo** de la web de NirKanA y está pensado para ser **privado**. Lo único público es una copia de lo que ya se
ve en nirkana.es: el repositorio `nirkana-sitio`. Hasta que el dominio pase a ese repositorio (ver [`notas/TRASPASO.md`](notas/TRASPASO.md)),
nirkana.es sigue saliendo del repositorio antiguo y este es público; no guardes aquí nada que no pueda verse.

- `docs/`: la web y la demo en `docs/demo/`. **Todo lo que hay aquí acaba en nirkana.es**: nada de notas, código de apoyo ni datos.
- `notas/`: cómo se mantiene la web ([`notas/WEB.md`](notas/WEB.md)) y el traspaso de lo público a lo privado
  ([`notas/TRASPASO.md`](notas/TRASPASO.md)). No se publican.
- `ops/`: comprobación diaria del sitio, generadores (guías, herramientas, textos legales), `publicar_sitio.py` (copia a la parte
  pública solo lo permitido) y `publico/` (README y flujo de la copia pública).
- `tests/`: pruebas de que la web solo promete lo que la app hace, de que sus herramientas funcionan y de que en `docs/` solo hay
  archivos de la web.
- `legal/`: plantillas de los textos legales (los datos reales del titular nunca se suben: `legal/datos.json` está en `.gitignore`).

El código de la aplicación NirKanA es privado y no está en este repositorio.

© NirKanA. Todos los derechos reservados (ver `LICENSE`).
