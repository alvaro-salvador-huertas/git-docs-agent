"""Localiza citas en las notas archivadas de una ejecución, sin evaluar su sentido."""

import argparse
from collections import Counter
from contextlib import contextmanager
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import re
import stat
import sys


# Lista propia y fija: el auditor no importa ni ejecuta el agente.
ALLOWED = {f"docs/git-{name}.md": f"git-{name}.md"
           for name in ("status", "add", "commit", "diff", "push")}
MAX_BYTES = 2 * 1024 * 1024
SPACE = r"\s*"
SECTION = r"sección\s+«(?P<section>[^«»\r\n]+)»\s*:\s*"
QUOTE = r"«(?P<fragment>[^«»]+)»"
CITATION_START = r"(?<!`)`(?P<file>[^`\r\n]+)`(?!`)" + SPACE + "—" + SPACE
CITATION = re.compile(CITATION_START + SECTION + QUOTE)
CONTINUATION = re.compile(r"[ \t]*;[ \t]*(?:" + SECTION + r")?" + QUOTE)
# Dentro de código solo se avisa ante una forma explícita de cita, incluso si
# está incompleta; mencionar un archivo Markdown por sí solo no es suficiente.
FENCED_HINT = re.compile(CITATION_START + r"sección\b")
FENCED_DETAIL = (
    "Cita formal dentro de un bloque cercado: puede ser un ejemplo de formato; "
    "revisión manual pendiente. No se comprueba su localización."
)
# Son avisos conservadores, no otra gramática que pueda validar citas.
HINT = re.compile(
    r"`[^`\r\n]*\.md[^`\r\n]*`|(?<![^\s`«»\[\]<>])[^\s`«»\[\]<>]+\.md\b"
    r"|\bsecci[oó]n[ \t]*[«\"“:]|;[ \t]*[«\"“]",
    re.IGNORECASE,
)
HEADING = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.+?)[ \t]*$")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


@dataclass
class Finding:
    estado: str
    linea: int
    archivo: str | None = None
    seccion: str | None = None
    fragmento: str | None = None
    detalle: str = ""


def normalize(text: str) -> str:
    """Solo negrita **...** emparejada en una línea y espacios consecutivos."""
    text = re.sub(r"\*\*([^*\r\n]+)\*\*", r"\1", text)
    return " ".join(text.split())


def sections(markdown: str) -> list[tuple[str, str]]:
    """Encabezados ATX fuera de cercas; cada cuerpo incluye subsecciones."""
    lines = markdown.splitlines(keepends=True)
    headings = []
    fence = None
    for index, line in enumerate(lines):
        marker = FENCE.match(line.rstrip("\r\n"))
        if fence is not None:
            if marker:
                run, tail = marker.groups()
                if run[0] == fence[0] and len(run) >= len(fence) and not tail.strip():
                    fence = None
            continue
        if marker:
            run, tail = marker.groups()
            if run[0] != "`" or "`" not in tail:
                fence = run
                continue
        heading = HEADING.match(line.rstrip("\r\n"))
        if heading:
            level, title = heading.groups()
            title = re.sub(r"[ \t]+#+[ \t]*$", "", title)
            headings.append((index, len(level), normalize(title)))
    result = []
    for position, (start, level, title) in enumerate(headings):
        end = next((i for i, depth, _ in headings[position + 1:] if depth <= level), len(lines))
        result.append((title, normalize("".join(lines[start + 1:end]))))
    return result


def fenced_regions(text: str):
    """Tramos contiguos (inicio, fin, es_bloque), sin borrar ni unir texto."""
    start = offset = 0
    fence = None
    for line in text.splitlines(keepends=True):
        marker = FENCE.match(line.rstrip("\r\n"))
        if marker:
            run, tail = marker.groups()
            if fence is None:
                if run[0] != "`" or "`" not in tail:
                    if start < offset:
                        yield start, offset, False
                    start, fence = offset, run
            elif run[0] == fence[0] and len(run) >= len(fence) and not tail.strip():
                yield start, offset + len(line), True
                start, fence = offset + len(line), None
        offset += len(line)
    if start < offset:
        yield start, offset, fence is not None


def extract(answer: str) -> list[Finding]:
    findings = []
    covered = bytearray(len(answer))
    unknown_lines = set()
    for region_start, region_end, in_fence in fenced_regions(answer):
        state = "cita_en_bloque" if in_fence else "por_comprobar"
        detail = FENCED_DETAIL if in_fence else ""
        for match in CITATION.finditer(answer, region_start, region_end):
            # Una cita puede contener literalmente otra; no interpretarla dos veces.
            if covered[match.start()]:
                continue
            file, section, fragment = match.group("file", "section", "fragment")
            start, end = match.span()
            findings.append(Finding(state, answer.count("\n", 0, start) + 1,
                                    file, section, fragment, detalle=detail))
            while continuation := CONTINUATION.match(answer, end, region_end):
                # La herencia nunca cruza un salto de línea, ni siquiera en un campo.
                if "\n" in continuation.group() or "\r" in continuation.group():
                    break
                section = continuation.group("section") or section
                findings.append(Finding(state, answer.count("\n", 0, end) + 1,
                                        file, section, continuation.group("fragment"), detalle=detail))
                end = continuation.end()
            covered[start:end] = b"\1" * (end - start)

        hints = FENCED_HINT if in_fence else HINT
        for hint in hints.finditer(answer, region_start, region_end):
            if not all(covered[hint.start():hint.end()]):
                line = answer.count("\n", 0, hint.start()) + 1
                if in_fence:
                    findings.append(Finding("cita_en_bloque", line, hint.group("file"),
                                            detalle=FENCED_DETAIL))
                else:
                    unknown_lines.add(line)
    for line in sorted(unknown_lines):
        findings.append(Finding("formato_no_reconocido", line, detalle=(
            "Referencia fuera de la gramática admitida; revisión manual pendiente."
        )))
    if not findings:
        findings.append(Finding("sin_citas", 1, detalle=(
            "No se detectaron citas. Una abstención puede ser correcta; revisar manualmente."
        )))
    return sorted(findings, key=lambda finding: finding.linea)


class EvidenceError(Exception):
    """Archivo esperado ausente, inseguro, ilegible o demasiado grande."""


@contextmanager
def open_directory(name, *, parent=None):
    descriptor = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
    try:
        yield descriptor
    finally:
        os.close(descriptor)


def read_regular(parent: int, name: str) -> str:
    # NONBLOCK evita esperar si un archivo esperado se ha sustituido por una FIFO.
    descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
    with os.fdopen(descriptor, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise EvidenceError("Se requiere un archivo regular sin enlace simbólico.")
        if info.st_size > MAX_BYTES:
            raise EvidenceError("El archivo supera el límite de 2 MiB.")
        content = stream.read(MAX_BYTES + 1)
        if len(content) > MAX_BYTES:
            raise EvidenceError("El archivo supera el límite de 2 MiB.")
        return content.decode("utf-8")


def check(finding: Finding, root: int, cache: dict) -> None:
    if finding.estado != "por_comprobar":
        return
    # Nunca se pasa una ruta tomada de la respuesta a open().
    if finding.archivo not in ALLOWED:
        finding.estado = "archivo_no_permitido"
        finding.detalle = "La ruta no coincide exactamente con una de las cinco notas permitidas."
        return
    if finding.archivo not in cache:
        try:
            with open_directory("docs", parent=root) as docs:
                content = read_regular(docs, ALLOWED[finding.archivo])
            cache[finding.archivo] = sections(content)
        except (OSError, UnicodeError, EvidenceError):
            cache[finding.archivo] = None
    archived = cache[finding.archivo]
    if archived is None:
        finding.estado = "evidencia_ausente"
        finding.detalle = (
            "Falta evidencia utilizable: nota archivada ausente, ilegible, no regular, "
            "con enlace simbólico o mayor de 2 MiB. No se sustituye por otra fuente."
        )
        return
    matches = [body for title, body in archived if title == normalize(finding.seccion)]
    if not matches:
        finding.estado = "seccion_inexistente"
    elif len(matches) > 1:
        finding.estado = "seccion_ambigua"
    elif not normalize(finding.fragmento):
        finding.estado = "formato_no_reconocido"
        finding.detalle = "Fragmento vacío tras normalizar; revisión manual pendiente."
    elif normalize(finding.fragmento) not in matches[0]:
        finding.estado = "fragmento_no_encontrado"
        finding.detalle = "No aparece en la sección indicada; otras secciones no validan la cita."
    else:
        finding.estado = "localizada"
        finding.detalle = "Fragmento localizado; respaldo semántico pendiente de revisión humana."


def audit(run: Path) -> dict:
    # El argumento del operador define la raíz; los descendientes se abren por
    # descriptor sin seguir symlinks, evitando escapes y carreras resolve/open.
    root_path = run.resolve(strict=True)
    with open_directory(root_path) as root:
        answer = read_regular(root, "respuesta.md")
        if not answer.strip():
            raise EvidenceError("respuesta.md está vacía; no equivale a una abstención.")
        findings = extract(answer)
        cache = {}
        for finding in findings:
            check(finding, root, cache)
    counts = dict(Counter(finding.estado for finding in findings))
    return {
        "resultados": [asdict(finding) for finding in findings],
        "resumen": counts,
        "revision_semantica": "pendiente: comprobar respaldo, contexto, cobertura y abstención",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ejecucion", type=Path, help="Directorio de la ejecución archivada")
    arguments = parser.parse_args(argv)
    try:
        report = audit(arguments.ejecucion)
    except (OSError, UnicodeError, EvidenceError) as error:
        print(json.dumps({"error": "entrada_no_utilizable", "detalle": str(error)},
                         ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if set(report["resumen"]) == {"localizada"} else 1


if __name__ == "__main__":
    sys.exit(main())
