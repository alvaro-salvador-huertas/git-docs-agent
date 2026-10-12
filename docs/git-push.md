# git push

Notas del proyecto basadas en fuentes oficiales. Este resumen propio no es documentación oficial de Git.

## Qué hace

Actualiza referencias, como ramas, en un repositorio remoto a partir del local y transfiere los datos necesarios que falten en el destino.

## Conceptos necesarios

- **Remoto:** repositorio de destino, identificado por un nombre configurado o una URL.
- **Rama:** referencia a un commit; permite publicar una línea de historial local.

## Ejemplo básico

Ejemplo explicativo, no ejecutado:

```bash
git push origin main
```

Suponiendo un remoto `origin` configurado y una rama local `main`, intentaría actualizar la rama `main` del destino con ese historial.

## Confusiones frecuentes

No crea commits ni publica ediciones sin commit, aunque estén preparadas. No envía necesariamente todas las ramas. El destino puede rechazar la actualización.

## Fuente y fecha de consulta

Fuente: [manual oficial de git-push](https://git-scm.com/docs/git-push), secciones DESCRIPTION, OPTIONS y OUTPUT.

Consulta realizada: **2026-10-12** (Europe/Madrid).
