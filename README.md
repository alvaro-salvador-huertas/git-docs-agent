# git-docs-agent

Proyecto de aprendizaje sobre agentes de IA y evaluación de sus respuestas.

**Estado: fase de diseño, con el primer hito preparado.** La documentación local y los casos de evaluación están disponibles. El prototipo no está implementado y todos los casos siguen pendientes de ejecución.

## Objetivo

Crear un asistente de terminal que responda preguntas sobre Git utilizando un conjunto pequeño de documentación local seleccionada y citando las fuentes que respaldan cada respuesta.

## Primera versión prevista

El asistente deberá:

- Recibir una pregunta del usuario por ejecución.
- Utilizar Codex CLI como motor del agente.
- Consultar documentación local seleccionada sobre `git status`, `git add`, `git commit`, `git diff` y `git push`.
- Responder indicando los archivos consultados y los fragmentos concretos que respaldan sus afirmaciones, con una referencia que permita localizarlos, como una sección o un rango de líneas.
- Reconocer cuándo la documentación disponible no permite responder, explicando qué información falta sin inventar respuestas ni citas.
- Guardar un registro de la ejecución que permita investigar errores: pregunta, documentación consultada, respuesta, citas y errores observados.

El alcance inicial se limita a explicar comandos. Ejecutar acciones que modifiquen repositorios queda fuera de esta versión.

## Archivos preparados

Las cinco fuentes oficiales se pudieron consultar el **2026-10-12** (Europe/Madrid). Cada nota contiene un resumen propio en español, conceptos, un ejemplo explicado sin ejecutar, confusiones frecuentes y la URL y fecha de consulta. Son notas del proyecto basadas en fuentes oficiales, no documentación oficial de Git.

| Archivo | Contenido y uso |
| --- | --- |
| [docs/git-status.md](docs/git-status.md) | Nota sobre el estado de los archivos; fuente del agente. |
| [docs/git-add.md](docs/git-add.md) | Nota sobre la preparación de contenido; fuente del agente. |
| [docs/git-commit.md](docs/git-commit.md) | Nota sobre la creación de commits locales; fuente del agente. |
| [docs/git-diff.md](docs/git-diff.md) | Nota sobre las dos comparaciones básicas; fuente del agente. |
| [docs/git-push.md](docs/git-push.md) | Nota sobre la publicación en un remoto; fuente del agente. |
| [evals/casos.md](evals/casos.md) | Cinco casos con ideas esperadas, referencias y condiciones de fallo; material exclusivo de evaluación. |

El conjunto de fuentes del agente se limita a esos cinco documentos de `docs/`. El README y los criterios de `evals/casos.md` no forman parte de ese conjunto. Las URL de las notas documentan su procedencia; no amplían la documentación local disponible para responder.

## Evaluación prevista

Se revisarán tres aspectos de las respuestas:

- **Corrección:** si la explicación responde a la pregunta sin errores sobre el comportamiento de Git.
- **Respaldo de las citas:** si los archivos y fragmentos citados existen, son localizables y sustentan las afirmaciones de la respuesta.
- **Reconocimiento de información insuficiente:** si el asistente detecta los límites de la documentación y evita completar las lagunas con afirmaciones sin respaldo.

### Cinco preguntas de ejemplo

Estas preguntas están desarrolladas en [evals/casos.md](evals/casos.md); **no representan pruebas ejecutadas ni resultados obtenidos**. Se evaluará el significado, sin exigir una redacción literal. La revisión documental confirma cobertura para las cuatro primeras y falta de información para la quinta.

1. ¿Qué información muestra `git status` sobre los archivos de un repositorio?
2. ¿Qué diferencia hay entre `git add` y `git commit` al guardar cambios?
3. ¿Qué diferencia hay entre `git diff` y `git diff --staged`?
4. ¿Qué hace `git push` y cómo se relaciona con los commits locales?
5. ¿Cómo puedo resolver un conflicto durante un `git rebase`? Este caso comprobará el reconocimiento de información insuficiente: las notas preparadas no incluyen un procedimiento de resolución.

## Hitos

1. **Documentación y casos de evaluación — preparado.** Cinco notas basadas en fuentes oficiales consultadas y cinco casos definidos con ideas esperadas, secciones de respaldo y condiciones de fallo. Se ha revisado la cobertura, incluido el caso de información insuficiente; los casos no se han ejecutado.
2. **Prototipo local que responda una pregunta — pendiente.** Integrar Codex CLI para recibir una pregunta, consultar los documentos seleccionados, emitir una respuesta con citas o reconocer la falta de información y guardar el registro de la ejecución.
3. **Evaluación de resultados y mejoras basadas en los fallos encontrados — pendiente.** Ejecutar los casos preparados, revisar los tres criterios, investigar los fallos mediante los registros y repetir los casos afectados tras introducir mejoras.

## Siguiente paso

Desarrollar el prototipo del segundo hito: una ejecución local con una pregunta, acceso a las cinco notas de `docs/`, respuesta con citas o reconocimiento de información insuficiente y registro para investigar errores. Los criterios de evaluación deberán permanecer fuera de las fuentes proporcionadas al agente.
