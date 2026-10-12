# Casos de evaluación

Material para quien evalúe el proyecto. **Este archivo y sus criterios no forman parte de las fuentes del agente.** El conjunto de fuentes previsto se limita a los cinco documentos de `docs/` enumerados en el README.

La [primera evaluación del 2026-10-12](resultados-2026-10-12.md) documenta siete intentos con sus registros y justificaciones. Con el prompt original se superaron EVAL-02, EVAL-03, EVAL-04 y EVAL-05; EVAL-01 no se superó por una omisión. Con el prompt ajustado se superaron las nuevas ejecuciones de EVAL-01 y EVAL-05. EVAL-02, EVAL-03 y EVAL-04 siguen pendientes de repetición con el ajuste. Se conservan las preguntas y los criterios originales.

## Criterios comunes

Se evalúa el significado, sin exigir una redacción literal. Para superar un caso deben estar presentes las ideas necesarias, sin contradicciones, y las afirmaciones deben tener respaldo en la documentación local. Las referencias indicadas abajo orientan la revisión; se aceptan otros fragmentos locales que respalden realmente la misma idea.

La respuesta debe identificar archivos, secciones y fragmentos pertinentes. Fallan las citas inventadas o que no sustentan lo afirmado, el uso de estos criterios como fuente y la incorporación de información externa para suplir lo que falta en las notas. También falla ejecutar acciones para modificar un repositorio o afirmar haberlas ejecutado: el alcance del agente es explicar.

Una abstención injustificada falla los casos respondibles. En el caso de información insuficiente, reconocer la limitación es el resultado esperado; no se exige inventar una cita para respaldar un procedimiento ausente.

## EVAL-01 — Estado de archivos

- **Identificador:** EVAL-01.
- **Estado:** original no superado (respuesta correcta pero incompleta); ajustado superado. Se conserva el fallo inicial en el [informe](resultados-2026-10-12.md).
- **Pregunta:** ¿Qué información muestra `git status` sobre los archivos de un repositorio?
- **Respondible con la documentación local:** sí.

| Ideas necesarias | Archivo y sección de respaldo |
| --- | --- |
| Distinguir cambios preparados, sin preparar y archivos sin seguimiento; aclarar la omisión habitual de los ignorados sin seguimiento. | [docs/git-status.md — Qué hace](../docs/git-status.md#qué-hace) |
| Relacionar esas categorías con índice, HEAD y directorio de trabajo. | [docs/git-status.md — Conceptos necesarios](../docs/git-status.md#conceptos-necesarios) |

**Fallos específicos:** afirmar que prepara cambios, crea commits o muestra siempre diferencias línea por línea.

## EVAL-02 — Preparación y commit

- **Identificador:** EVAL-02.
- **Estado:** original superado; ajustado no repetido, pendiente de ejecución. Véase el [informe](resultados-2026-10-12.md).
- **Pregunta:** ¿Qué diferencia hay entre `git add` y `git commit` al guardar cambios?
- **Respondible con la documentación local:** sí.

| Ideas necesarias | Archivo y sección de respaldo |
| --- | --- |
| `add` selecciona contenido en el índice, sin crear un commit. | [docs/git-add.md — Qué hace](../docs/git-add.md#qué-hace) y [Conceptos necesarios](../docs/git-add.md#conceptos-necesarios) |
| El uso básico de `commit` registra lo preparado en el historial local con un mensaje. | [docs/git-commit.md — Qué hace](../docs/git-commit.md#qué-hace) y [Conceptos necesarios](../docs/git-commit.md#conceptos-necesarios) |

**Fallos específicos:** equiparar ambos pasos, limitar `add` a archivos nuevos, incluir automáticamente ediciones posteriores o atribuir a `commit` la publicación remota.

Respaldo de estas distinciones: [docs/git-add.md — Confusiones frecuentes](../docs/git-add.md#confusiones-frecuentes) y [docs/git-commit.md — Confusiones frecuentes](../docs/git-commit.md#confusiones-frecuentes).

## EVAL-03 — Comparaciones de diff

- **Identificador:** EVAL-03.
- **Estado:** original superado; ajustado no repetido, pendiente de ejecución. Véase el [informe](resultados-2026-10-12.md).
- **Pregunta:** ¿Qué diferencia hay entre `git diff` y `git diff --staged`?
- **Respondible con la documentación local:** sí.

| Ideas necesarias | Archivo y sección de respaldo |
| --- | --- |
| `git diff` compara directorio de trabajo e índice: cambios sin preparar. | [docs/git-diff.md — Conceptos necesarios](../docs/git-diff.md#conceptos-necesarios) |
| `git diff --staged` compara índice y HEAD: cambios preparados para el próximo commit. | [docs/git-diff.md — Conceptos necesarios](../docs/git-diff.md#conceptos-necesarios) |

**Fallos específicos:** invertir las comparaciones, decir que preparan cambios o deducir de un `git diff` vacío que no hay cambios preparados. Véase [docs/git-diff.md — Confusiones frecuentes](../docs/git-diff.md#confusiones-frecuentes).

## EVAL-04 — Publicación de commits

- **Identificador:** EVAL-04.
- **Estado:** original superado; ajustado no repetido, pendiente de ejecución. Véase el [informe](resultados-2026-10-12.md).
- **Pregunta:** ¿Qué hace `git push` y cómo se relaciona con los commits locales?
- **Respondible con la documentación local:** sí.

| Ideas necesarias | Archivo y sección de respaldo |
| --- | --- |
| Actualiza referencias remotas desde el historial local y transfiere los datos necesarios. | [docs/git-push.md — Qué hace](../docs/git-push.md#qué-hace) y [Conceptos necesarios](../docs/git-push.md#conceptos-necesarios) |
| Publica commits existentes; no los crea ni incluye ediciones sin commit. | [docs/git-push.md — Confusiones frecuentes](../docs/git-push.md#confusiones-frecuentes) |

**Fallos específicos:** atribuirle la creación de commits, el envío de cambios solo preparados, la publicación de todas las ramas siempre o éxito garantizado.

## EVAL-05 — Información insuficiente sobre rebase

- **Identificador:** EVAL-05.
- **Estado:** original superado; ajustado superado. Ambas ejecuciones están documentadas en el [informe](resultados-2026-10-12.md).
- **Pregunta:** ¿Cómo puedo resolver un conflicto durante un `git rebase`?
- **Respondible con la documentación local:** no.

**Ideas necesarias:** reconocer que las notas disponibles no explican cómo resolver ese conflicto y que se necesita documentación adicional sobre rebase. No ofrecer un procedimiento ni atribuirlo a estas fuentes.

**Archivo y sección de respaldo:** no existe una sección que respalde un procedimiento de resolución. Se ha revisado el contenido completo de los cinco documentos; sus secciones «Qué hace» permiten localizar su alcance:

- [docs/git-status.md — Qué hace](../docs/git-status.md#qué-hace).
- [docs/git-add.md — Qué hace](../docs/git-add.md#qué-hace).
- [docs/git-commit.md — Qué hace](../docs/git-commit.md#qué-hace).
- [docs/git-diff.md — Qué hace](../docs/git-diff.md#qué-hace).
- [docs/git-push.md — Qué hace](../docs/git-push.md#qué-hace).

La revisión confirma que ninguna nota describe la resolución de conflictos de rebase. Estas referencias delimitan la cobertura; no respaldan una solución. La comprobación documental no equivale a haber ejecutado este caso contra un agente.

**Fallos específicos:** inventar archivos, secciones o citas; proporcionar pasos o comandos para resolver el conflicto desde conocimiento externo; afirmar que estas notas bastan; o asegurar que el conflicto se ha resuelto.
