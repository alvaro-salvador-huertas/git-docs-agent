# git-docs-agent

Proyecto de aprendizaje sobre agentes de IA y evaluación de sus respuestas.

**Estado: prototipo local implementado, con una primera evaluación real documentada.** Se han revisado siete intentos: cinco con el prompt original y dos con un ajuste de cobertura conceptual. El fallo inicial de EVAL-01 se conserva; EVAL-02, EVAL-03 y EVAL-04 aún no se han repetido con el prompt ajustado. Véase el [informe del 2026-10-12](evals/resultados-2026-10-12.md).

## Objetivo

Crear un asistente de terminal que responda preguntas sobre Git utilizando un conjunto pequeño de documentación local seleccionada y citando las fuentes que respaldan cada respuesta.

## Alcance del prototipo

El prototipo recibe una pregunta, prepara un contexto local con cinco notas y llama a Codex CLI. Sus instrucciones piden:

- Leer únicamente las notas necesarias sobre `git status`, `git add`, `git commit`, `git diff` y `git push`.
- Responder en español, respaldando las afirmaciones con archivo, sección y un fragmento breve de la nota.
- Reconocer la información insuficiente sin completar lagunas con conocimiento externo.
- Explicar sin ejecutar comandos Git ni modificar repositorios.

El programa conserva el registro de cada ejecución para investigar errores. La primera revisión manual ha comprobado respuestas y citas en los casos ejecutados y ha motivado un ajuste del prompt; esta evidencia limitada no demuestra fiabilidad general.

## Ejecución

Requisitos: **Python 3.12** y **Codex CLI** disponible como `codex` en `PATH`, con su autenticación y modelo ya configurados. El programa utiliza únicamente la biblioteca estándar de Python. La ayuda local de Codex CLI 0.162.1 confirma las opciones utilizadas.

Desde la carpeta del proyecto:

```bash
python3 git_docs_agent.py "¿Qué diferencia hay entre git add y git commit?"
```

Desde una carpeta hermana del proyecto, indica la ruta relativa al script:

```bash
python3 ../git-docs-agent/git_docs_agent.py "¿Qué hace git status?"
```

Las notas, las instrucciones y `runs/` se localizan respecto al archivo del programa, no respecto a la carpeta desde la que se ejecuta. La pregunta debe ir como un único argumento; una cadena vacía o formada solo por espacios se rechaza antes de crear un registro.

El programa crea un directorio temporal fuera del proyecto, con solo los cinco archivos permitidos dentro de `docs/`. No copia README, evaluaciones, pruebas ni otros archivos. Si falta una nota, informa del problema sin llamar a Codex. El temporal se elimina al finalizar normalmente o al gestionar un fallo.

La invocación se construye como una lista de argumentos equivalente a:

```text
codex exec --sandbox read-only --ephemeral --skip-git-repo-check --json --color never -c 'approval_policy="never"' -c 'web_search="disabled"' -C <carpeta-temporal> -o <ruta-absoluta-a-runs/ejecucion/respuesta.md> -
```

Las comillas simples del ejemplo solo agrupan los valores; las comillas dobles de `"never"` y `"disabled"` se conservan en los argumentos de configuración. `subprocess.run` usa `shell=False`, transmite las instrucciones y la pregunta por stdin en bloques separados y no añade opciones de modelo ni cambia configuración, credenciales o reglas globales. La pregunta se codifica como una cadena JSON para distinguirla del bloque de instrucciones.

El límite es de **180 segundos** por llamada a Codex, definido en `TIMEOUT_SECONDS`. Se gestionan la ausencia del ejecutable, un código de salida no nulo, el tiempo agotado y una respuesta final ausente o vacía. En caso de éxito se muestra la respuesta y la ruta del registro; en caso de fallo, un mensaje claro y esa ruta. Los códigos del programa son `0` para éxito técnico, `1` para fallo de ejecución o registro y `2` para argumentos inválidos.

## Registros

Cada pregunta válida crea una carpeta única `runs/<fecha-UTC>-<sufijo>/`, salvo que no sea posible escribir el registro. Contiene:

| Archivo | Contenido |
| --- | --- |
| `pregunta.txt` | Pregunta original. |
| `docs/` | Copia exacta en bytes de las cinco notas disponibles en el contexto preparado. |
| `entrada.txt` | Instrucciones y pregunta tal como se enviaron por stdin. |
| `eventos.jsonl` | Bytes originales de stdout; no se filtran ni se reinterpretan. |
| `errores.txt` | Bytes originales de stderr. |
| `respuesta.md` | Respuesta producida por Codex; puede quedar vacía o parcial si hay un fallo. |
| `metadatos.json` | Fechas UTC, duración, argumentos, límite, estado, código de salida o motivo del fallo. |

Si falla la preparación, se conserva lo que haya podido registrarse: puede no existir todavía `docs/` o `entrada.txt`. Los errores del programa se guardan en los metadatos; `errores.txt` se reserva para stderr de Codex. Si Codex termina sin crear `respuesta.md`, el programa deja ese archivo vacío y registra el motivo. Un fallo de escritura puede impedir completar el registro.

`documentos_disponibles` enumera el contexto preparado. **`documentos_consultados` queda en `null`: no se deduce que el agente haya leído las cinco notas.** Las lecturas efectivas deben investigarse en `eventos.jsonl`. El estado actual `completada` (denominado `correcta` en los dos primeros registros) significa que Codex terminó con código cero y entregó texto, no que su respuesta sea correcta sobre Git.

El programa no copia credenciales ni serializa variables de entorno. Conserva la salida de Codex sin modificarla. `runs/`, `__pycache__/` y `*.pyc` están excluidos de Git mediante `.gitignore`.

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
| [evals/resultados-2026-10-12.md](evals/resultados-2026-10-12.md) | Primera evaluación: siete intentos, versiones del prompt, evidencias y límites; material exclusivo de evaluación. |
| [git_docs_agent.py](git_docs_agent.py) | Programa de terminal, preparación del contexto, llamada a Codex y registro. |
| [prompts/responder.md](prompts/responder.md) | Instrucciones de respuesta y límites del agente. |
| [tests/test_git_docs_agent.py](tests/test_git_docs_agent.py) | Pruebas del programa con un proceso simulado, sin llamadas reales a Codex. |

El conjunto de fuentes del agente se limita a esos cinco documentos de `docs/`. El README y todo el material de `evals/`, incluidos criterios e informes, no forman parte de ese conjunto. Las URL de las notas documentan su procedencia; no amplían la documentación local disponible para responder.

## Limitaciones reales

**Una carpeta temporal y el modo `read-only` no garantizan aislamiento completo de lectura del sistema.** Copiar solo cinco notas delimita el contexto preparado, pero no impide técnicamente toda lectura de otros archivos accesibles a Codex. La restricción de consultar únicamente las notas también depende de las instrucciones y de que el modelo las respete. La configuración y las reglas de Codex ya existentes siguen vigentes.

La búsqueda web se desactiva en esta invocación. El programa no valida automáticamente citas, hechos, lecturas ni abstenciones, y no interpreta los eventos. Un registro con éxito técnico no demuestra calidad. Las notas son breves y no cubren procedimientos de resolución de conflictos de rebase.

## Pruebas del programa

```bash
python3 -m unittest discover -s tests -v
```

**Las 12 pruebas unitarias terminaron correctamente según la ejecución aportada por el usuario.** Sustituyen `subprocess.run` por un proceso simulado; no llaman a Codex. Comprueban el contexto sin archivos de evaluación, preguntas vacías, notas ausentes, opciones de invocación, éxito, errores, tiempo agotado, respuestas ausentes o vacías, registros únicos y uso desde otra carpeta. Los registros de estas pruebas se crean en proyectos temporales de prueba.

Estas pruebas verifican el comportamiento del programa; **no evalúan la calidad de respuestas de un modelo**. Sus resultados se distinguen de la evaluación manual del agente documentada a continuación. No se han vuelto a ejecutar para redactar el informe.

## Primera evaluación del agente

Se han revisado tres aspectos de las respuestas según la rúbrica original:

- **Corrección:** si la explicación responde a la pregunta sin errores sobre el comportamiento de Git.
- **Respaldo de las citas:** si los archivos y fragmentos citados existen, son localizables y sustentan las afirmaciones de la respuesta.
- **Reconocimiento de información insuficiente:** si el asistente detecta los límites de la documentación y evita completar las lagunas con afirmaciones sin respaldo.

El [informe del 2026-10-12](evals/resultados-2026-10-12.md) detalla los siete intentos. Con el prompt original se superaron EVAL-02, EVAL-03, EVAL-04 y EVAL-05. EVAL-01 respondió correctamente, pero omitió las relaciones entre índice, HEAD y directorio de trabajo exigidas por la rúbrica, aunque el registro confirma la lectura de la nota.

Tras añadir una instrucción general de cobertura conceptual, las nuevas ejecuciones de EVAL-01 y EVAL-05 superaron sus casos. **EVAL-02, EVAL-03 y EVAL-04 no se han repetido con el prompt ajustado.** Son pocas preguntas y una ejecución por caso y versión evaluada; no se atribuye al ajuste el resultado completo del prompt original ni se considera demostrada una fiabilidad general.

Los registros completos permanecen locales en `runs/`, excluidos de Git. El informe conserva identificadores, lecturas y fragmentos relevantes para entender los resultados; sus enlaces a registros solo funcionan donde se conserven esos archivos.

### Cinco preguntas de evaluación

Las preguntas y los criterios originales se conservan en [evals/casos.md](evals/casos.md), con estados separados por versión del prompt. La evaluación considera el significado, sin exigir una redacción literal. La documentación cubre las cuatro primeras; la quinta comprueba el reconocimiento de información insuficiente.

1. ¿Qué información muestra `git status` sobre los archivos de un repositorio?
2. ¿Qué diferencia hay entre `git add` y `git commit` al guardar cambios?
3. ¿Qué diferencia hay entre `git diff` y `git diff --staged`?
4. ¿Qué hace `git push` y cómo se relaciona con los commits locales?
5. ¿Cómo puedo resolver un conflicto durante un `git rebase`? Las notas preparadas no incluyen un procedimiento de resolución; las dos ejecuciones revisadas reconocieron esa limitación.

## Hitos

1. **Documentación y casos de evaluación — preparado.** Cinco notas basadas en fuentes oficiales consultadas y cinco casos con sus preguntas y criterios originales conservados.
2. **Prototipo local que responda una pregunta — implementado y ejecutado.** Programa de terminal con contexto temporal, instrucciones, llamada a Codex y registros; pruebas unitarias con proceso simulado superadas y primeras ejecuciones reales registradas.
3. **Evaluación de resultados y mejoras basadas en los fallos encontrados — en curso.** Primera revisión de cinco casos con el prompt original, omisión identificada y ajuste general del prompt; EVAL-01 y EVAL-05 repetidos con éxito. Faltan las repeticiones de EVAL-02, EVAL-03 y EVAL-04 con el ajuste y una evaluación más amplia.

## Siguiente paso

Repetir EVAL-02, EVAL-03 y EVAL-04 con el prompt ajustado, conservando los resultados anteriores. Después, ampliar las preguntas y repeticiones para estudiar los fallos y la variabilidad. Los criterios e informes de evaluación deben permanecer fuera de las fuentes proporcionadas al agente.
