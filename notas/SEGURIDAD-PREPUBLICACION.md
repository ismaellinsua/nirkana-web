# NirKanA — checklist de seguridad antes de publicar

## Alcance
- Web comercial y demo: solo los archivos de `docs/` se publican (GitHub Pages desde la carpeta `/docs`); el resto no sale en `nirkana.es` (`tests/web-publico.test.mjs` y `ops/publicar_sitio.py` impiden que una nota, código o datos acaben en `docs/`).
- La demo usa exclusivamente datos ficticios, sin conexión a la base de datos comercial.
- `nirkana-app` y su repositorio, credenciales y base de datos permanecen separados.
- La prueba de 24 horas debe tener base de datos y credenciales independientes.

## Secretos y datos
- El único repositorio público es `nirkana-sitio` (GitHub Pages gratuito), y solo lleva lo que ya se ve en nirkana.es: nada que no deba verse puede estar en él. El trabajo de la web, `nirkana-app` (código, credenciales y datos) y el producto anterior son privados.
- Nunca incorporar `.env`, certificados, claves, contraseñas ni datos reales de clientes a Git.
- Utilizar secretos del proveedor de alojamiento para variables privadas del servidor.
- Verificar historial de commits, artefactos CI, logs, archivos estáticos y backups.
- Si una clave estuvo expuesta, revocarla/rotarla; añadirla a `.gitignore` no corrige la exposición anterior.
- No incluir secretos en variables de entorno del navegador ni en archivos JS públicos.

## Controles antes del lanzamiento
- Revisar HTTPS y las cabeceras que de verdad envía GitHub Pages (no deja poner cabeceras propias: la CSP va en una etiqueta `<meta>`).
- Probar CSP y formulario de contacto sin bloquear funciones legítimas.
- Probar XSS, CSRF, IDOR y aislamiento entre negocios con dos cuentas distintas.
- Comprobar permisos del lado del servidor en cada operación sensible.
- Verificar cookies HttpOnly/Secure/SameSite, cierre de sesión, expiración y recuperación de contraseña.
- Asegurar que la falta de configuración de Stripe no conceda acceso comercial no autorizado.
- Comprobar dependencias, copias cifradas, restauración y registro sin datos sensibles.
- No activar Veri*Factu ni cobros reales sin validación integral.

## Procedimiento
1. Auditar código y configuración en una rama; registrar hallazgos reproducibles.
2. Añadir pruebas que fallen antes del arreglo y pasen después.
3. Revisar cambios y CI; fusionar solo con autorización.
4. Desplegar primero en entorno de prueba; verificar rutas web y demo.
5. Desplegar producción, comprobar errores y conservar plan de reversión.

> Esta lista no certifica seguridad. Las verificaciones de infraestructura y secretos deben hacerse también en las cuentas de GitHub, Render y Neon.
