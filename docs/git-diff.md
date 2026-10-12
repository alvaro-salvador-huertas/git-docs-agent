# git diff

Notas del proyecto basadas en fuentes oficiales. Este resumen propio no es documentación oficial de Git.

## Qué hace

Muestra diferencias de contenido. Estas notas cubren dos comparaciones básicas.

## Conceptos necesarios

El **directorio de trabajo** contiene tus archivos; el **índice**, lo preparado; **HEAD** identifica el commit actual.

- `git diff`: compara directorio de trabajo e índice; muestra cambios sin preparar.
- `git diff --staged`: compara índice y HEAD; muestra cambios preparados. Antes del primer commit muestra todo lo preparado.

## Ejemplo básico

Ejemplo explicativo, no ejecutado:

```bash
git diff --staged
```

Permitiría revisar las diferencias preparadas para el próximo commit. Las ediciones posteriores a la preparación aparecerían en `git diff`.

## Confusiones frecuentes

Una salida vacía de `git diff` no descarta cambios preparados. Ninguna de estas comparaciones prepara cambios ni crea commits.

## Fuente y fecha de consulta

Fuente: [manual oficial de git-diff](https://git-scm.com/docs/git-diff), sección DESCRIPTION, formas básica y `--cached` (sinónimo de `--staged`).

Consulta realizada: **2026-10-12** (Europe/Madrid).
