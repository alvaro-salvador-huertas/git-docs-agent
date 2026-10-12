# git commit

Notas del proyecto basadas en fuentes oficiales. Este resumen propio no es documentación oficial de Git.

## Qué hace

En el uso básico, crea un commit local con el contenido del índice y un mensaje descriptivo. Si estás en una rama, esta pasa a señalar el nuevo commit.

## Conceptos necesarios

- **Índice:** contenido preparado previamente, por ejemplo mediante `git add`.
- **Commit:** registro de una versión del proyecto en su historial.
- **Mensaje:** descripción del cambio registrado.

## Ejemplo básico

Ejemplo explicativo, no ejecutado:

```bash
git commit -m "Documenta el objetivo"
```

Con cambios ya preparados, crearía un commit con ellos. `-m` proporciona el mensaje.

## Confusiones frecuentes

Este uso no incorpora automáticamente cambios sin preparar. Crear un commit local no publica los cambios en un repositorio remoto.

## Fuente y fecha de consulta

Fuente: [manual oficial de git-commit](https://git-scm.com/docs/git-commit), secciones DESCRIPTION y OPTIONS (`-m`).

Consulta realizada: **2026-10-12** (Europe/Madrid).
