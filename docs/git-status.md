# git status

Notas del proyecto basadas en fuentes oficiales. Este resumen propio no es documentación oficial de Git.

## Qué hace

Informa de cambios preparados para el próximo commit, cambios sin preparar y archivos sin seguimiento. Por defecto, omite los archivos sin seguimiento que están ignorados.

## Conceptos necesarios

- **Directorio de trabajo:** archivos que editas.
- **Índice o área de preparación:** contenido seleccionado para el próximo commit.
- **HEAD:** commit actual, cuando existe.
- Los cambios preparados comparan índice y HEAD; los no preparados comparan directorio de trabajo e índice. Un archivo sin seguimiento todavía no figura en el índice.

## Ejemplo básico

Ejemplo explicativo, no ejecutado:

```bash
git status
```

Permitiría distinguir un archivo modificado sin preparar de otro ya preparado, sin crear un commit.

## Confusiones frecuentes

Un archivo puede tener cambios preparados y otros posteriores sin preparar. El resumen de estado no muestra, por defecto, las diferencias línea por línea.

## Fuente y fecha de consulta

Fuente: [manual oficial de git-status](https://git-scm.com/docs/git-status), secciones DESCRIPTION, OPTIONS y OUTPUT.

Consulta realizada: **2026-10-12** (Europe/Madrid).
