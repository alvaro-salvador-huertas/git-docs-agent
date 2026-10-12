# Primera evaluación de git-docs-agent — 2026-10-12

Se documentan siete intentos ya realizados y revisados en la sesión: cinco con el prompt original y dos con el ajustado. Los resultados aportados por el usuario se han contrastado con los registros locales y la [rúbrica de los casos](casos.md). Para redactar este informe no se han realizado nuevas consultas al agente ni se han vuelto a ejecutar las pruebas unitarias.

El prompt original superó EVAL-02, EVAL-03, EVAL-04 y EVAL-05. **EVAL-01 original no superó la rúbrica: su respuesta fue correcta, pero incompleta.** Con el prompt ajustado se superaron las nuevas ejecuciones de EVAL-01 y EVAL-05. EVAL-02, EVAL-03 y EVAL-04 no se han repetido con ese ajuste; sus resultados originales no se trasladan a la nueva versión.

## Qué se evaluó y cómo

Se revisaron las cinco preguntas de [casos.md](casos.md), sin cambiar preguntas ni criterios: corrección y cobertura de las ideas necesarias, respaldo de las citas y reconocimiento de información insuficiente. La valoración fue semántica y manual, sin exigir una redacción literal.

Para cada intento se contrastaron:

- `pregunta.txt` y `entrada.txt`: pregunta y versión de las instrucciones realmente enviadas.
- `respuesta.md` y la copia de `docs/`: afirmaciones, citas y cobertura de la rúbrica.
- `eventos.jsonl`: comandos de lectura completados y contenido devuelto.
- `metadatos.json` y `errores.txt`: resultado técnico de la ejecución.

Las siete carpetas contienen las mismas cinco notas, idénticas en bytes entre ejecuciones y respecto a las notas actuales de `docs/`. Todos los intentos terminaron con código de salida `0`, sin motivo de fallo técnico y con `errores.txt` vacío. Los estados técnicos registrados son `correcta` en los dos primeros intentos cronológicos y `completada` en los restantes. Esos estados no califican la calidad: EVAL-01 original terminó técnicamente bien y no superó la evaluación.

## Versiones del prompt

La clasificación se hizo comparando el bloque de instrucciones de cada `entrada.txt`, separado de la pregunta. Se encontraron exactamente dos variantes:

- **Original:** compartida por los cinco primeros intentos. Puede consultarse en la [entrada de EVAL-02 original](../runs/20261012T165828992792Z-rpwjph9v/entrada.txt).
- **Ajustado:** compartida por los dos intentos posteriores. La [entrada de EVAL-01 ajustado](../runs/20261012T194804390904Z-auhvqnhl/entrada.txt) incorpora este único párrafo adicional al inicio de «Respuesta y citas»:

> Responde todas las partes de la pregunta con una explicación breve pero
> suficiente para alguien que está aprendiendo Git. Explica los conceptos
> y las relaciones que las notas presentan como necesarios para entender
> la respuesta. Si enumeras categorías, aclara qué significan y cómo se
> diferencian cuando esa distinción sea relevante. Mantén todo ese contexto
> respaldado por las fuentes permitidas. Si falta documentación, conserva
> esa limitación en lugar de completar la explicación con conocimiento externo.

El ajuste pide cobertura conceptual de forma general y mantiene el límite de las fuentes. No incorpora los casos ni su rúbrica. El resto de las instrucciones se conserva. La versión de cada intento se atribuye a su `entrada.txt`, no al contenido actual de `prompts/responder.md`.

## Los siete intentos

Los identificadores corresponden a las carpetas bajo `runs/`; los enlaces llevan a sus respuestas locales. La `Z` de los identificadores indica UTC.

| Caso | Prompt | Identificador de ejecución | Resultado | Justificación breve |
| --- | --- | --- | --- | --- |
| EVAL-01 | Original | [20261012T193310287068Z-_33o73t0](../runs/20261012T193310287068Z-_33o73t0/respuesta.md) | **No superado: incompleto** | Enumera las categorías y la omisión de ignorados, con citas válidas, pero omite las relaciones entre índice, HEAD y directorio de trabajo exigidas por la rúbrica. |
| EVAL-02 | Original | [20261012T165828992792Z-rpwjph9v](../runs/20261012T165828992792Z-rpwjph9v/respuesta.md) | Superado | Distingue preparar contenido en el índice de crear el commit local con lo preparado y un mensaje; cita ambas notas. |
| EVAL-03 | Original | [20261012T193330830079Z-lu035uh_](../runs/20261012T193330830079Z-lu035uh_/respuesta.md) | Superado | Explica directorio de trabajo frente a índice e índice frente a HEAD, con citas; no confunde salida vacía con ausencia de cambios preparados. |
| EVAL-04 | Original | [20261012T193350209422Z-y5828_em](../runs/20261012T193350209422Z-y5828_em/respuesta.md) | Superado | Explica la actualización remota desde el historial local y que push no crea commits ni publica ediciones sin commit; aporta respaldo local. |
| EVAL-05 | Original | [20261012T192455743184Z-bq3cxq4l](../runs/20261012T192455743184Z-bq3cxq4l/respuesta.md) | Superado | Reconoce que faltan instrucciones sobre conflictos de rebase; la cita sobre status se limita a su función general, sin inventar un procedimiento. |
| EVAL-01 | Ajustado | [20261012T194804390904Z-auhvqnhl](../runs/20261012T194804390904Z-auhvqnhl/respuesta.md) | Superado | Añade las definiciones y relaciones que faltaban, citando «Conceptos necesarios», y conserva las categorías y la aclaración sobre ignorados. |
| EVAL-05 | Ajustado | [20261012T194907360274Z-0q4d8he8](../runs/20261012T194907360274Z-0q4d8he8/respuesta.md) | Superado | Mantiene la abstención ante la falta de documentación de rebase; no convierte la explicación general de add en pasos para resolver el conflicto. |

## Lecturas registradas relevantes

En todos los metadatos figuran cinco `documentos_disponibles` y `documentos_consultados: null`. Las siguientes lecturas se acreditan por eventos `item.completed` de tipo `command_execution`, con código `0` y el texto de las notas en `aggregated_output`. Las líneas indicadas son las del archivo JSONL; no se deducen las lecturas de la lista de archivos disponibles.

| Intento | Lecturas completadas en `eventos.jsonl` |
| --- | --- |
| [EVAL-01 original](../runs/20261012T193310287068Z-_33o73t0/eventos.jsonl) | Línea 5, `item_1`: `cat docs/git-status.md`. |
| [EVAL-02 original](../runs/20261012T165828992792Z-rpwjph9v/eventos.jsonl) | Línea 5, `item_1`: `cat docs/git-add.md`; línea 7, `item_2`: `cat docs/git-commit.md`. |
| [EVAL-03 original](../runs/20261012T193330830079Z-lu035uh_/eventos.jsonl) | Línea 5, `item_1`: `cat docs/git-diff.md`. |
| [EVAL-04 original](../runs/20261012T193350209422Z-y5828_em/eventos.jsonl) | Línea 5, `item_1`: `cat docs/git-commit.md`; línea 7, `item_2`: `cat docs/git-push.md`. |
| [EVAL-05 original](../runs/20261012T192455743184Z-bq3cxq4l/eventos.jsonl) | Línea 5, `item_1`: una lectura conjunta de las cinco notas. |
| [EVAL-01 ajustado](../runs/20261012T194804390904Z-auhvqnhl/eventos.jsonl) | Línea 5, `item_1`: `cat docs/git-status.md`. |
| [EVAL-05 ajustado](../runs/20261012T194907360274Z-0q4d8he8/eventos.jsonl) | Línea 5, `item_1`: una lectura conjunta de las cinco notas. |

La lectura conjunta de ambos intentos de EVAL-05 fue `cat docs/git-status.md docs/git-add.md docs/git-commit.md docs/git-diff.md docs/git-push.md`. Los comandos se muestran aquí como evidencia registrada, sin ejecutarlos de nuevo. No aparecen comandos Git ni lecturas de otros archivos en los eventos de ejecución de comandos revisados; esto no demuestra aislamiento de lectura del sistema.

## Omisión detectada y resultado del ajuste

La respuesta original de EVAL-01 enumeró «Cambios preparados», «Cambios sin preparar» y «Archivos sin seguimiento», explicó la omisión habitual de ignorados y citó «Qué hace» y «Confusiones frecuentes». No explicó qué comparaciones daban lugar a esas categorías.

La rúbrica ya exigía relacionarlas con índice, HEAD y directorio de trabajo. Además, la lectura registrada de `git-status.md` incluía la sección [Conceptos necesarios](../docs/git-status.md#conceptos-necesarios), con este respaldo:

> Los cambios preparados comparan índice y HEAD; los no preparados comparan directorio de trabajo e índice.

La evidencia sitúa el fallo en la cobertura de la respuesta: la información estaba disponible y su lectura quedó registrada. El intento original permanece como **no superado por omisión**, aunque las afirmaciones que sí incluyó eran correctas.

Tras incorporar la instrucción general de cobertura conceptual, la nueva respuesta de EVAL-01 incluyó:

> **Cambios preparados:** diferencias entre el índice y HEAD.
>
> **Cambios sin preparar:** diferencias entre el directorio de trabajo y el índice.

También definió los tres conceptos, explicó los archivos sin seguimiento y citó la sección correspondiente. La nueva ejecución superó el caso.

Se repitió EVAL-05 para comprobar si la petición de una explicación más completa conservaba el reconocimiento de límites. La respuesta ajustada afirmó: «Las cinco notas permitidas no documentan `git rebase` ni la resolución de conflictos». Citó una función general de add y aclaró que las notas no explican su uso durante un rebase; no proporcionó pasos. El caso volvió a superarse.

La mejora observada en EVAL-01 y la abstención mantenida en EVAL-05 solo describen esos dos intentos posteriores. No se ha comprobado el resultado del ajuste en EVAL-02, EVAL-03 o EVAL-04.

## Pruebas del programa y evaluación del agente

Según la ejecución aportada por el usuario, **las 12 pruebas unitarias terminaron correctamente**. Usan un proceso simulado y comprueban el comportamiento del programa: preparación del contexto, entrada, invocación, errores, tiempo agotado y registros. Ese resultado no mide la calidad de las respuestas del modelo.

Los siete intentos de este informe son ejecuciones reales ya existentes, revisadas manualmente frente a la rúbrica. Evalúan respuestas, citas y reconocimiento de información insuficiente. El fallo inicial de EVAL-01 muestra por qué pasar las pruebas unitarias y obtener código de salida cero no basta para superar un caso del agente.

## Alcance de la evidencia y límites

- Solo se han usado cinco preguntas de un conjunto pequeño de documentación.
- Hay una ejecución por combinación de caso y versión evaluada; no se ha medido variabilidad mediante repeticiones de la misma combinación.
- Del prompt ajustado solo se han evaluado EVAL-01 y EVAL-05. No existe un resultado de cinco casos superados para esa versión.
- Una mejora en una única ejecución no permite atribuir con certeza todo el cambio al prompt ni demuestra fiabilidad general.
- La valoración es manual. Las lecturas registradas acreditan acceso al texto, pero por sí solas no garantizan su uso correcto ni la cobertura de la respuesta.
- Una carpeta temporal y `read-only` **no garantizan aislamiento completo de lectura del sistema**. Las instrucciones restringen las fuentes, pero estas pruebas no demuestran que todo acceso externo sea técnicamente imposible.

Los registros completos permanecen locales en `runs/`, excluidos de Git mediante [.gitignore](../.gitignore). Los enlaces relativos a esos registros solo funcionarán donde se conserven las carpetas locales; este informe incluye los identificadores, las lecturas y los fragmentos relevantes para entender los resultados sin publicar los registros completos. El informe y la rúbrica son material de evaluación, fuera de las fuentes del agente.

El siguiente trabajo pendiente es repetir EVAL-02, EVAL-03 y EVAL-04 con el prompt ajustado y ampliar las repeticiones antes de extraer conclusiones más generales.
