# git add

Notas del proyecto basadas en fuentes oficiales. Este resumen propio no es documentación oficial de Git.

## Qué hace

Prepara contenido de archivos nuevos o modificados en el índice para el próximo commit.

## Conceptos necesarios

El **directorio de trabajo** contiene los archivos editables. El **índice**, también llamado área de preparación, guarda el contenido seleccionado. Preparar ese contenido todavía no crea un commit.

## Ejemplo básico

Ejemplo explicativo, no ejecutado:

```bash
git add notas.txt
```

Suponiendo que `notas.txt` existe y no está ignorado, prepararía su contenido actual. No incluiría automáticamente las ediciones posteriores.

## Confusiones frecuentes

- No sirve únicamente para archivos nuevos: también prepara modificaciones.
- Si editas después, debes volver a preparar los cambios que quieras incluir.
- Preparar cambios y registrarlos mediante un commit son pasos distintos.

## Fuente y fecha de consulta

Fuente: [manual oficial de git-add](https://git-scm.com/docs/git-add), sección DESCRIPTION.

Consulta realizada: **2026-10-12** (Europe/Madrid).
