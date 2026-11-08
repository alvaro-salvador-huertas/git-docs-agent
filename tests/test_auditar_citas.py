"""Ejemplos sintéticos: existencia textual, límites de lectura y revisión pendiente."""

from contextlib import chdir, redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import auditar_citas as auditor


NOTE = """# git add

## Qué hace

Prepara contenido en el **índice** para el próximo commit.
Preparar ese contenido todavía no crea un commit.

## Conceptos necesarios

El **directorio de trabajo** contiene los archivos editables.
El índice guarda el contenido seleccionado.

### Detalle

Una subsección pertenece a su sección superior.

## Ejemplo

```markdown
## Qué hace
Esto no es un encabezado real.
```

~~~markdown
## Qué hace
~~~
"""


def citation(fragment="Prepara contenido en el **índice**", section="Qué hace",
             file="docs/git-add.md"):
    return f'`{file}` — sección «{section}»: «{fragment}».'


class AuditorTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="auditor-citas-tests-")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.run = self.base / "run"
        (self.run / "docs").mkdir(parents=True)
        self.note = self.run / "docs/git-add.md"
        self.note.write_text(NOTE, encoding="utf-8")
        self.answer = self.run / "respuesta.md"

    def audit(self, answer):
        self.answer.write_text(answer, encoding="utf-8")
        return auditor.audit(self.run)

    def states(self, answer):
        return [item["estado"] for item in self.audit(answer)["resultados"]]

    def test_valid_citation_uses_archived_note(self):
        self.assertEqual(self.states(citation()), ["localizada"])

    def test_invented_fragment(self):
        self.assertEqual(self.states(citation("Publica todos los commits")),
                         ["fragmento_no_encontrado"])

    def test_real_fragment_in_wrong_section(self):
        self.assertEqual(self.states(citation("El índice guarda el contenido seleccionado.")),
                         ["fragmento_no_encontrado"])

    def test_outside_paths_are_never_opened(self):
        outside = self.base / "secreto.md"
        outside.write_text(NOTE, encoding="utf-8")
        paths = ("../secreto.md", str(outside), "docs/../../secreto.md",
                 "docs/../docs/git-add.md", "docs/extra.md", "docs/git-add.md#qué-hace",
                 "https://example.invalid/git-add.md", "docs\\git-add.md",
                 "./docs/git-add.md", "docs/git-add.md/otra.md")
        for path in paths:
            with self.subTest(path=path), patch.object(auditor.os, "open", wraps=os.open) as opened:
                self.assertEqual(self.states(citation(file=path)), ["archivo_no_permitido"])
                self.assertEqual([call.args[0] for call in opened.call_args_list],
                                 [self.run.resolve(), "respuesta.md"])

    def test_abstention_without_citations_needs_human_review(self):
        report = self.audit("Las notas no explican rebase. Falta documentación para responder.")
        self.assertEqual(report["resumen"], {"sin_citas": 1})
        self.assertIn("pendiente", report["revision_semantica"])

    def test_existing_quote_does_not_support_the_claim(self):
        # La afirmación contradice la cita: localizarla no puede aprobar la respuesta.
        report = self.audit("git add crea un commit y publica los cambios. " + citation(
            "Preparar ese contenido todavía no crea un commit."))
        self.assertEqual(report["resumen"], {"localizada": 1})
        self.assertIn("pendiente", report["revision_semantica"])
        self.assertIn("semántico pendiente", report["resultados"][0]["detalle"])

    def test_missing_archive_is_not_replaced_by_current_repo_note(self):
        self.note.unlink()
        self.assertEqual(self.states(citation()), ["evidencia_ausente"])

    def test_missing_docs_directory(self):
        self.note.unlink()
        self.note.parent.rmdir()
        self.assertEqual(self.states(citation()), ["evidencia_ausente"])

    def test_missing_and_duplicate_sections(self):
        self.assertEqual(self.states(citation(section="No existe")), ["seccion_inexistente"])
        self.note.write_text(NOTE + "\n## Qué hace\nOtra sección.\n", encoding="utf-8")
        self.assertEqual(self.states(citation()), ["seccion_ambigua"])

    def test_section_boundaries_and_subsections(self):
        fragment = "Una subsección pertenece a su sección superior."
        self.assertEqual(self.states(citation(fragment, "Conceptos necesarios")), ["localizada"])
        self.assertEqual(self.states(citation(fragment, "Detalle")), ["localizada"])
        self.assertEqual(self.states(citation(fragment, "Qué hace")), ["fragmento_no_encontrado"])
        self.assertEqual(self.states(citation("Qué hace")), ["fragmento_no_encontrado"])

    def test_heading_levels_closing_hashes_and_fences(self):
        self.note.write_text("# Nota\n## **Título** ##\nTexto.\n### Hija\nOtro.\n"
                             "## Siguiente\nFuera.\n", encoding="utf-8")
        self.assertEqual(self.states(citation("Texto.", "Título")), ["localizada"])
        self.assertEqual(self.states(citation("Fuera.", "Título")), ["fragmento_no_encontrado"])
        # Las dos cercas de NOTE no crean títulos duplicados.
        self.note.write_text(NOTE, encoding="utf-8")
        self.assertEqual(self.states(citation()), ["localizada"])

    def test_whitespace_and_bold_only_are_normalized(self):
        self.assertEqual(self.states(citation("Prepara  contenido\nen el índice")), ["localizada"])
        for fragment in ("prepara contenido", "Prepara contenido en el indice",
                         "Prepara … próximo commit", "Prepara contenido en el `índice`",
                         "Prepara contenido en el *índice*"):
            with self.subTest(fragment=fragment):
                self.assertEqual(self.states(citation(fragment)), ["fragmento_no_encontrado"])

    def test_chained_fragments_and_sections_each_produce_a_result(self):
        answer = citation().removesuffix(".") + (
            "; «Preparar ese contenido todavía no crea un commit.»; "
            "sección «Conceptos necesarios»: «El índice guarda el contenido seleccionado.»"
        )
        self.assertEqual(self.states(answer), ["localizada"] * 3)
        answer += "; «Fragmento inventado»"
        self.assertEqual(self.states(answer), ["localizada"] * 3 + ["fragmento_no_encontrado"])

    def test_chain_does_not_inherit_across_lines(self):
        self.assertEqual(self.states(citation().removesuffix(".") +
                                     ";\nsección «Conceptos necesarios»: «El índice»"),
                         ["localizada", "formato_no_reconocido"])

    def test_complete_citation_can_span_lines_and_records_line_number(self):
        answer = "Introducción.\n\n`docs/git-add.md`\n— sección «Qué hace»:\n«Prepara contenido»"
        result = self.audit(answer)["resultados"][0]
        self.assertEqual((result["estado"], result["linea"]), ("localizada", 3))

    def test_same_citation_in_prose_and_fences_has_different_status_and_exit_code(self):
        for fence in ("```", "~~~"):
            for fenced in (False, True):
                with self.subTest(fence=fence, fenced=fenced):
                    answer = citation()
                    if fenced:
                        answer = f"Ejemplo:\n{fence}markdown\n{answer}\n{fence}\n"
                    self.answer.write_text(answer, encoding="utf-8")
                    with redirect_stdout(io.StringIO()) as output:
                        self.assertEqual(auditor.main([str(self.run)]), 1 if fenced else 0)
                    report = json.loads(output.getvalue())
                    result, = report["resultados"]
                    self.assertEqual(result["estado"], "cita_en_bloque" if fenced else "localizada")
                    self.assertEqual(result["linea"], 3 if fenced else 1)
                    if fenced:
                        self.assertIn("ejemplo", result["detalle"])
                        self.assertIn("pendiente", result["detalle"])

    def test_mixed_response_preserves_lines_and_does_not_validate_code_citations(self):
        for fence in ("```", "~~~"):
            with self.subTest(fence=fence):
                answer = ("Introducción.\n" + citation() + "\n\n" + fence + "markdown\n" +
                          citation() + "\n" + fence + "\n\n" +
                          '`docs/git-add.md`\n— sección «Qué hace»:\n«Prepara contenido»')
                self.answer.write_text(answer, encoding="utf-8")
                with redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(auditor.main([str(self.run)]), 1)
                results = json.loads(output.getvalue())["resultados"]
                self.assertEqual([(item["estado"], item["linea"]) for item in results],
                                 [("localizada", 2), ("cita_en_bloque", 5), ("localizada", 8)])

    def test_ordinary_markdown_paths_in_code_do_not_add_warnings(self):
        for fence in ("```", "~~~"):
            with self.subTest(fence=fence):
                block = f'{fence}python\npath = "docs/git-add.md"\n# `README.md`\n{fence}\n'
                self.assertEqual(self.states(citation() + "\n" + block), ["localizada"])
                self.assertEqual(self.states(block), ["sin_citas"])
                self.assertEqual(self.states(block + "`docs/git-add.md`"), ["formato_no_reconocido"])

    def test_fenced_citations_and_their_continuations_do_not_read_notes(self):
        for fence in ("```", "~~~"):
            with self.subTest(fence=fence), patch.object(auditor.os, "open", wraps=os.open) as opened:
                answer = (fence + "markdown\n" + citation().removesuffix(".") +
                          "; «Preparar ese contenido todavía no crea un commit.»; "
                          "sección «Conceptos necesarios»: «El índice»\n" + fence)
                report = self.audit(answer)
                self.assertEqual(report["resumen"], {"cita_en_bloque": 3})
                self.assertEqual([item["linea"] for item in report["resultados"]], [2, 2, 2])
                self.assertEqual([call.args[0] for call in opened.call_args_list],
                                 [self.run.resolve(), "respuesta.md"])

    def test_multiline_citations_cannot_cross_fence_boundaries(self):
        for fence in ("```", "~~~"):
            for before, after in (
                ('`docs/git-add.md`', '— sección «Qué hace»: «Prepara contenido»'),
                ('`docs/git-add.md` —', 'sección «Qué hace»: «Prepara contenido»'),
                ('`docs/git-add.md` — sección «Qué hace»:', '«Prepara contenido»'),
                ('`docs/git-add.md` — sección «Qué hace»: «Prepara', 'contenido»'),
            ):
                for answer in (
                    before + "\n" + fence + "\n\n" + fence + "\n" + after,
                    before + "\n" + fence + "\n" + after + "\n" + fence,
                    fence + "\n" + before + "\n" + fence + "\n" + after,
                ):
                    with self.subTest(fence=fence, answer=answer):
                        self.assertFalse(any(item.estado == "por_comprobar"
                                             for item in auditor.extract(answer)))

    def test_continuations_cannot_inherit_across_fences(self):
        for fence in ("```", "~~~"):
            with self.subTest(fence=fence):
                answer = (citation() + "\n" + fence + "\n# Ejemplo\n" + fence +
                          '\n; sección «Conceptos necesarios»: «El índice»')
                results = self.audit(answer)["resultados"]
                self.assertEqual([(item["estado"], item["linea"]) for item in results],
                                 [("localizada", 1), ("formato_no_reconocido", 5)])
                answer = fence + "\n" + citation() + "\n" + fence + '\n; «Prepara contenido»'
                self.assertEqual(self.states(answer), ["cita_en_bloque", "formato_no_reconocido"])

    def test_fence_lengths_indentation_closing_rules_and_unclosed_block(self):
        for fence in ("````", "~~~~"):
            with self.subTest(fence=fence):
                # Una cerca más corta, de otro tipo o con texto no cierra el bloque.
                other = "~~~" if fence[0] == "`" else "```"
                answer = ("   " + fence + "markdown\n" + fence[:3] + "\n" + other + "\n" +
                          fence + " texto\n" + citation() + "\n  " + fence + fence[0] +
                          "\n" + citation())
                results = self.audit(answer)["resultados"]
                self.assertEqual([(item["estado"], item["linea"]) for item in results],
                                 [("cita_en_bloque", 5), ("localizada", 7)])
                self.assertEqual(self.states(fence + "\n" + citation()), ["cita_en_bloque"])

    def test_fenced_formal_prefix_is_pending_but_plain_file_is_ignored(self):
        for fence in ("```", "~~~"):
            with self.subTest(fence=fence):
                answer = (fence + '\n`docs/git-add.md` — sección «Qué hace».\n' +
                          'cat docs/git-add.md\n' + fence)
                results = self.audit(answer)["resultados"]
                self.assertEqual([(item["estado"], item["linea"]) for item in results],
                                 [("cita_en_bloque", 2)])

    def test_unsupported_formats_remain_pending(self):
        for answer in (
            '`docs/git-add.md` — sección «Qué hace».',
            '`docs/git-add.md` — sección "Qué hace": "Prepara contenido".',
            'docs/git-add.md — sección «Qué hace»: «Prepara contenido».',
            '[nota](docs/git-add.md#qué-hace): «Prepara contenido».',
            citation().replace("—", "-"),
            citation().replace("`docs/git-add.md`", "``docs/git-add.md``"),
            citation(fragment=""),
            citation(fragment="   "),
        ):
            with self.subTest(answer=answer):
                self.assertTrue(all(state == "formato_no_reconocido" for state in self.states(answer)))

    def test_valid_citation_does_not_hide_an_unknown_reference(self):
        self.assertEqual(self.states(citation() + '\n[otra](docs/git-commit.md)'),
                         ["localizada", "formato_no_reconocido"])

    def test_symlinked_notes_and_docs_are_not_followed(self):
        outside = self.base / "externa.md"
        outside.write_text(NOTE, encoding="utf-8")
        self.note.unlink()
        self.note.symlink_to(outside)
        self.assertEqual(self.states(citation()), ["evidencia_ausente"])
        self.note.unlink()
        self.note.parent.rmdir()
        external_docs = self.base / "external-docs"
        external_docs.mkdir()
        (external_docs / "git-add.md").write_text(NOTE, encoding="utf-8")
        self.note.parent.symlink_to(external_docs, target_is_directory=True)
        self.assertEqual(self.states(citation()), ["evidencia_ausente"])

    def test_non_regular_invalid_utf8_and_oversized_notes(self):
        for content in (b"\xff", b"x" * (auditor.MAX_BYTES + 1)):
            self.note.write_bytes(content)
            self.assertEqual(self.states(citation()), ["evidencia_ausente"])
        self.note.unlink()
        os.mkfifo(self.note)
        self.assertEqual(self.states(citation()), ["evidencia_ausente"])

    def test_cli_reports_json_and_exit_codes_from_another_directory(self):
        for answer, expected in ((citation(), 0), (citation("Inventado"), 1),
                                 ("No puedo responder con estas notas.", 1)):
            self.answer.write_text(answer, encoding="utf-8")
            with chdir(self.base), redirect_stdout(io.StringIO()) as output:
                self.assertEqual(auditor.main([str(self.run)]), expected)
            self.assertIn("revision_semantica", json.loads(output.getvalue()))

    def test_cli_rejects_unusable_answer(self):
        outside = self.base / "respuesta-externa.md"
        outside.write_text(citation(), encoding="utf-8")
        for kind in ("missing", "empty", "invalid", "large", "directory", "fifo", "symlink"):
            with self.subTest(kind=kind):
                if kind == "empty":
                    self.answer.write_text(" \n", encoding="utf-8")
                elif kind == "invalid":
                    self.answer.write_bytes(b"\xff")
                elif kind == "large":
                    self.answer.write_bytes(b"x" * (auditor.MAX_BYTES + 1))
                elif kind == "directory":
                    self.answer.mkdir()
                elif kind == "fifo":
                    os.mkfifo(self.answer)
                elif kind == "symlink":
                    self.answer.symlink_to(outside)
                with redirect_stderr(io.StringIO()) as error, redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(auditor.main([str(self.run)]), 2)
                self.assertEqual(json.loads(error.getvalue())["error"], "entrada_no_utilizable")
                self.assertEqual(output.getvalue(), "")
                if self.answer.is_dir():
                    self.answer.rmdir()
                elif kind != "missing":
                    self.answer.unlink()


if __name__ == "__main__":
    unittest.main()
