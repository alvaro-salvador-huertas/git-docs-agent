# Auditor independiente de citas

## Criterio de éxito (fijado antes de implementar)

Una cita se considera **localizada**, exclusivamente en sentido mecánico, si
identifica exactamente uno de los cinco archivos permitidos, existe su copia
archivada en `docs/` de la ejecución, el título identifica una única sección y
el fragmento aparece de forma contigua dentro de su contenido. Encontrarlo en
otra sección no sirve. No se consultarán las notas actuales del proyecto para
suplir copias ausentes.

Se distinguirán localización, archivo no permitido, evidencia archivada ausente
o ilegible, sección inexistente, sección ambigua, fragmento no encontrado,
formato no reconocido y respuesta sin citas. La ausencia de citas queda
pendiente: una abstención puede ser correcta y no necesitar ninguna. Una
respuesta vacía o ilegible será un error de entrada, no una abstención.

El formato admitido parte del prompt actual:

```text
`docs/git-add.md` — sección «Qué hace»: «fragmento breve».
```

Se admitirán también las dos continuaciones observadas en los registros, solo
en la misma línea y separadas por punto y coma: `; sección «Otro título»:
«otro fragmento»` hereda el archivo y `; «otro fragmento»` hereda archivo y
sección. Cada fragmento produce un resultado independiente. Se permiten
espacios y saltos de línea entre los campos de una cita completa. Las comillas
deben ser angulares, la ruta debe ir entre un único par de backticks y el
separador debe ser una raya (`—`). No se interpretarán enlaces como fuentes.
Las referencias detectables a archivos Markdown o a secciones que no cumplan
esa gramática quedarán pendientes, incluso junto a otras citas localizadas.
No se promete detectar cualquier manera de citar en lenguaje natural.

Las secciones admitidas son encabezados ATX de Markdown (`#` a `######`),
ignorando encabezados dentro de bloques cercados con backticks o tildes. Su
contenido termina ante el siguiente encabezado del mismo nivel o superior;
incluye subsecciones. Dos encabezados con el mismo título dejan la referencia
ambigua, aunque solo uno contenga el fragmento. Los títulos y fragmentos se
compararán conservando mayúsculas, acentos, palabras y puntuación. Solo se
colapsarán secuencias de espacios (incluidos saltos de línea) a un espacio y
se retirarán pares de negrita `**texto**` en una misma línea, tanto en nota como
en cita. Los backticks de código se conservan. No se eliminarán otras marcas
Markdown ni se expandirán elipsis, paráfrasis o coincidencias aproximadas.

El auditor solo leerá `respuesta.md` y las notas permitidas que se citen bajo
el directorio indicado. No abrirá rutas extraídas libremente de la respuesta,
enlaces, metadatos, eventos ni archivos externos. Rechazará enlaces simbólicos
en `respuesta.md`, `docs/` y sus notas, y archivos que no sean regulares; tendrá
un límite de tamaño por archivo. El directorio indicado por el operador define
la raíz de la ejecución. No escribirá en ella.

**Revisión humana siempre pendiente:** si el fragmento realmente respalda lo
afirmado, si falta contexto o cobertura, si la abstención está justificada y
si las acciones del agente cumplieron sus instrucciones. Una cita existente
puede acompañar una afirmación falsa; localizarla nunca certifica esa afirmación.

## Citas en bloques cercados — regla añadida el 2026-11-08

En `respuesta.md`, una cita formal dentro de un bloque cercado queda como
`cita_en_bloque`: puede ser un ejemplo de formato y requiere revisión humana.
Se conservan sus campos y línea original, pero no se consulta la nota ni se
comprueba su localización. También se señala una referencia incompleta que
empiece con la ruta entre backticks, raya y `sección`. Una mención ordinaria a
un archivo `.md` dentro del bloque se ignora. Si solo hay código sin citas
formales, el resultado es `sin_citas`.

Se reconocen líneas con hasta tres espacios de sangría y al menos tres
backticks o tildes consecutivos, con una etiqueta opcional de lenguaje. Una
apertura de backticks no admite backticks en esa etiqueta. El cierre debe usar
el mismo carácter, al menos la longitud de apertura y ningún texto posterior
salvo espacios. Un bloque sin cierre llega al final de la respuesta. Es el mismo
subconjunto de cercas usado para reconocer encabezados en las notas; no es un
parser Markdown completo y no interpreta contenedores como listas o blockquotes.

Cada bloque y cada tramo de prosa se analizan por separado sobre sus posiciones
originales. Las citas multilínea y sus continuaciones quedan limitadas al tramo
en que empiezan: no pueden unir texto situado a ambos lados de una cerca. La
gramática y normalización en prosa se conservan. Una respuesta mixta puede tener
citas `localizada` y `cita_en_bloque`; estas últimas mantienen el código de salida
en **1** aunque existan otras localizadas.

## Evidencia disponible antes de implementar

El remoto local es `https://github.com/alvaro-salvador-huertas/git-docs-agent.git`.
Se leyeron README, prompt, programa, pruebas y los tres documentos de evaluación.
Hay trece ejecuciones locales archivadas; se inspeccionaron sus respuestas sin
modificarlas. EVAL-04 ajustado encadena secciones y omite tres marcas de negrita;
EVAL-08 encadena fragmentos de una sección. EVAL-01 ajustado incluye una
referencia a «Conceptos necesarios» sin fragmento adjunto, que requiere revisión
con este criterio aunque el informe manual considere correcta la respuesta.
EVAL-06 y EVAL-07 no contienen citas y su abstención fue favorable en la revisión
manual. Esta evidencia permite contrastar el auditor sin generar respuestas.

## Uso y salida

Desde la raíz del repositorio, con Python 3.12 en Linux/POSIX (se usan
descriptores relativos y `O_NOFOLLOW` para rechazar enlaces simbólicos):

```bash
python3 scripts/auditar_citas.py runs/<ejecucion>
python3 -m unittest discover -s tests -v
```

No requiere dependencias, Codex, autenticación ni conexión de red. Solo produce
JSON por stdout; los errores de entrada van por stderr. No guarda el informe ni
modifica la ejecución. Por ejemplo, al auditar
`runs/20261012T194907360274Z-0q4d8he8`, la salida es:

```json
{
  "resultados": [
    {
      "estado": "localizada",
      "linea": 3,
      "archivo": "docs/git-add.md",
      "seccion": "Conceptos necesarios",
      "fragmento": "Preparar ese contenido todavía no crea un commit",
      "detalle": "Fragmento localizado; respaldo semántico pendiente de revisión humana."
    }
  ],
  "resumen": {"localizada": 1},
  "revision_semantica": "pendiente: comprobar respaldo, contexto, cobertura y abstención"
}
```

Las líneas empiezan en 1. Cada fragmento encadenado tiene su propio resultado;
los avisos de formato se agrupan por línea. Los estados posibles son:

| Estado | Interpretación |
| --- | --- |
| `localizada` | Archivo permitido, sección única y fragmento localizado. |
| `archivo_no_permitido` | Ruta distinta de las cinco rutas exactas del prompt, sin abrirla. Incluye rutas absolutas, `..`, URL y variantes como `./docs/…`. |
| `evidencia_ausente` | Falta una copia archivada utilizable: ausente, ilegible, UTF-8 inválido, symlink, archivo no regular o mayor de 2 MiB. No se recurre al repositorio actual. |
| `seccion_inexistente` / `seccion_ambigua` | Ningún encabezado admitido coincide / hay más de uno. |
| `fragmento_no_encontrado` | No aparece en el cuerpo de esa sección tras la normalización documentada. |
| `formato_no_reconocido` | Referencia detectable no interpretable o fragmento vacío; pendiente manual. |
| `cita_en_bloque` | Cita formal o prefijo de cita dentro de una cerca; posible ejemplo, pendiente manual sin comprobar la nota. |
| `sin_citas` | No se detectaron referencias; pendiente manual, compatible con una abstención correcta. |

Código de salida **0**: todos los fragmentos detectados están localizados, sin
avisos de formato ni citas en bloques; **1**: hay incidencias o pendientes mecánicos, incluida la
ausencia de citas; **2**: argumentos inválidos o ejecución/respuesta no utilizable.
Ni 0 acredita corrección semántica ni 1 determina que la respuesta sea incorrecta.
La raíz es el directorio elegido por el operador, resuelto antes de abrirlo.
Las únicas lecturas de contenido son `respuesta.md` y las notas citadas de la
lista fija; los nombres procedentes de la respuesta nunca se abren directamente.
No se comprueba integridad histórica de las notas ni qué leyó realmente el agente.

## Validación realizada — 2026-11-07

Se ejecutaron las 33 pruebas unitarias: 21 nuevas del auditor y las 12 existentes,
todas correctas y sin llamadas a modelos ni red. Los ejemplos sintéticos cubren
las cinco situaciones solicitadas, secciones ausentes/duplicadas, cadenas de
citas, formatos desconocidos, normalización estricta, límites de sección,
symlinks, FIFO, UTF-8 inválido y tamaños excesivos. Un ejemplo afirma falsamente
que add crea y publica commits mientras cita literalmente «Preparar ese contenido
todavía no crea un commit.»: el resultado es `localizada`, con revisión semántica
pendiente. Es una limitación intencionada y comprobada.

Además se ejecutó el comando sobre las **13 ejecuciones históricas locales**,
comparando su resultado con los informes manuales del
[2026-10-12](resultados-2026-10-12.md) y
[2026-10-13](resultados-2026-10-13.md). Se comprobaron hashes SHA-256 antes y
después de los 78 archivos comprobados (respuesta y cinco notas por ejecución): sin
cambios. No se generaron nuevas respuestas ni se modificaron informes anteriores.

| Ejecución | Caso / variante | Resultado mecánico | Comparación con revisión manual |
| --- | --- | --- | --- |
| `20261012T165828992792Z-rpwjph9v` | EVAL-02 original | 2 localizadas | Coincide con la localización manual; el respaldo semántico sigue fuera del auditor. |
| `20261012T192455743184Z-bq3cxq4l` | EVAL-05 original | 1 localizada | La cita general de status existe; no demuestra un procedimiento de rebase. |
| `20261012T193310287068Z-_33o73t0` | EVAL-01 original | 3 localizadas | La revisión manual lo suspende por cobertura incompleta: localizar citas no resuelve esa omisión. |
| `20261012T193330830079Z-lu035uh_` | EVAL-03 original | 3 localizadas | Coincide con la localización manual. |
| `20261012T193350209422Z-y5828_em` | EVAL-04 original | 4 localizadas | Coincide con la localización manual. |
| `20261012T194804390904Z-auhvqnhl` | EVAL-01 ajustado | 4 localizadas, 1 formato pendiente (línea 11) | El informe lo aprueba semánticamente; la referencia sin fragmento adjunto requiere revisión con la gramática del auditor. Las definiciones anteriores no se asocian automáticamente. |
| `20261012T194907360274Z-0q4d8he8` | EVAL-05 ajustado | 1 localizada | La cita general de add existe; la abstención requiere valoración humana. |
| `20261013T135249258311Z-j7d34p96` | EVAL-02 ajustado | 5 localizadas | Coincide con los cinco fragmentos revisados manualmente. |
| `20261013T135338276408Z-jx_0o4no` | EVAL-03 ajustado | 4 localizadas | Coincide con los cuatro fragmentos revisados manualmente. |
| `20261013T135449724534Z-gcebbcoo` | EVAL-04 ajustado | 6 localizadas | Coincide con los seis del informe, incluidos tres que omiten negrita y la continuación que hereda archivo. |
| `20261013T140253245965Z-f3bf4zmc` | EVAL-06 exploratorio | Sin citas, pendiente | La revisión manual acepta la abstención; el auditor no la juzga. |
| `20261013T140340071884Z-czxlreey` | EVAL-07 exploratorio | Sin citas, pendiente | La revisión manual acepta la reconducción; el auditor no la juzga. |
| `20261013T140425148628Z-s9on516n` | EVAL-08 exploratorio | 6 localizadas | Coincide con los seis del informe, incluida la continuación que hereda sección. |

En total: **39 fragmentos localizados**, una referencia de formato pendiente y
dos respuestas sin citas. Los 21 fragmentos del informe del día 13 se localizaron;
la normalización de negrita explica sus tres diferencias de formato. Estos
resultados describen los registros disponibles, no la fiabilidad de futuras
respuestas ni la cobertura de todos los formatos posibles.

La herramienta ahorra buscar a mano cada fragmento en la copia archivada y
comprobar su archivo y sección. Una persona debe seguir leyendo la afirmación
y su contexto para decidir si la cita la respalda, si la respuesta está completa
y si corresponde abstenerse; también debe revisar los formatos pendientes.

## Regresión de bloques cercados — 2026-11-08

Antes de modificar el código se reprodujo el fallo con una nota archivada
sintética `docs/git-add.md`:

```markdown
## Qué hace

Prepara contenido en el índice.
```

Dos respuestas usan la misma cita. La primera contiene en prosa
`docs/git-add.md` — sección «Qué hace»: «Prepara contenido en el índice.».
La segunda contiene únicamente este bloque (también se probó con tildes):

````markdown
```markdown
`docs/git-add.md` — sección «Qué hace»: «Prepara contenido en el índice.».
```
````

| Respuesta sintética | Antes | Después |
| --- | --- | --- |
| Cita en prosa | `localizada`, línea 1, código 0 | Igual. |
| Misma cita en cerca de backticks | `localizada`, línea 2, código 0 | `cita_en_bloque`, línea 2, código 1. |
| Misma cita en cerca de tildes | `localizada`, línea 2, código 0 | `cita_en_bloque`, línea 2, código 1. |

Diagnóstico nuevo: «Cita formal dentro de un bloque cercado: puede ser un ejemplo
de formato; revisión manual pendiente. No se comprueba su localización.»

Se añadieron ocho pruebas de regresión, con subcasos para ambos tipos de cerca,
respuestas mixtas, números de línea, menciones ordinarias a `.md`, referencias
formales incompletas, continuaciones, límites de citas multilínea y cierres de
distinta longitud o ausentes. La suite local completa pasó: **41 pruebas**
(29 del auditor y las 12 existentes, con proceso simulado).

Se volvió a ejecutar únicamente el auditor sobre los **13 históricos**. Cada
ejecución conserva su resumen anterior: **39 localizadas, una referencia pendiente
y dos respuestas sin citas**. El pendiente sigue siendo la referencia sin
fragmento de EVAL-01 ajustado, línea 11; las respuestas sin citas siguen siendo
EVAL-06 y EVAL-07. No hay cambios que atribuir a la regla de cercas en esos registros.

Se compararon SHA-256 y el inventario completo de `runs/` antes y después:
los **143 archivos originales** conservan sus hashes. El agente, su prompt y los
cambios previos del README se conservaron en bytes. No se generaron respuestas
históricas ni se hicieron llamadas a modelos o a la red.
