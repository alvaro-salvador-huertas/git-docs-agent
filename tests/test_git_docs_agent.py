"""Pruebas del programa con un sustituto de subprocess.run; nunca usan Codex."""

from contextlib import chdir, redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import git_docs_agent as agent


class AgentTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="git-docs-agent-tests-")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.project = self.base / "project"
        self.project.mkdir()
        (self.project / "docs").mkdir()
        (self.project / "prompts").mkdir()
        original = Path(agent.__file__).resolve().parent
        for name in agent.DOCUMENTS:
            (self.project / "docs" / name).write_bytes((original / "docs" / name).read_bytes())
        (self.project / "prompts" / "responder.md").write_bytes(
            (original / "prompts" / "responder.md").read_bytes()
        )
        for name in ("README.md", "evals/casos.md", "tests/secreto.txt", "docs/extra.md"):
            path = self.project / name
            path.parent.mkdir(exist_ok=True)
            path.write_text("CONTENIDO_EXCLUIDO", encoding="utf-8")
        self.answer = "Respuesta simulada; no evalúa al modelo.\n"
        self.events = b'{"type":"evento_simulado"}\r\n'
        self.errors = b"diagnostico simulado\n\xff"
        self.workspaces = []
        process_patch = patch.object(agent.subprocess, "run", side_effect=self.simulate_success)
        self.process = process_patch.start()
        self.addCleanup(process_patch.stop)

    def simulate_success(self, command, *, input, stdout, stderr, cwd, shell, check, timeout):
        workspace = Path(cwd)
        self.workspaces.append(workspace)
        self.assertFalse(workspace.is_relative_to(self.project))
        self.assertEqual({path.name for path in workspace.iterdir()}, {"docs"})
        self.assertEqual({path.name for path in (workspace / "docs").iterdir()}, set(agent.DOCUMENTS))
        self.assertNotIn(b"CONTENIDO_EXCLUIDO", input)
        self.assertIs(shell, False)
        self.assertIs(check, False)
        self.assertEqual(timeout, 180)
        response = Path(command[command.index("-o") + 1])
        self.assertTrue(response.is_absolute())
        self.assertEqual(command, [
            "codex", "exec", "--sandbox", "read-only", "--ephemeral",
            "--skip-git-repo-check", "--json", "--color", "never",
            "-c", 'approval_policy="never"', "-c", 'web_search="disabled"',
            "-C", str(workspace), "-o", str(response), "-",
        ])
        for name in agent.DOCUMENTS:
            expected = (self.project / "docs" / name).read_bytes()
            self.assertEqual((workspace / "docs" / name).read_bytes(), expected)
            self.assertEqual((response.parent / "docs" / name).read_bytes(), expected)
        self.assertEqual((response.parent / "entrada.txt").read_bytes(), input)
        stdout.write(self.events)
        stderr.write(self.errors)
        response.write_text(self.answer, encoding="utf-8")
        return subprocess.CompletedProcess(command, 0)

    def metadata(self, result):
        return json.loads((result.directory / "metadatos.json").read_text(encoding="utf-8"))

    def assert_failure(self, result, reason, code=None):
        self.assertIsNotNone(result.error)
        metadata = self.metadata(result)
        self.assertEqual(metadata["estado"], "fallo")
        self.assertEqual(metadata["motivo_fallo"], reason)
        self.assertEqual(metadata["codigo_salida"], code)
        for name in ("pregunta.txt", "eventos.jsonl", "errores.txt", "respuesta.md"):
            self.assertTrue((result.directory / name).is_file())

    def test_success_keeps_exact_context_and_raw_outputs(self):
        question = '¿Qué hace add? "texto"\n$(no_ejecutar); fin'
        result = agent.execute_question(question, self.project)
        self.assertIsNone(result.error)
        self.assertEqual(result.answer, self.answer)
        self.assertEqual((result.directory / "pregunta.txt").read_text(), question)
        self.assertEqual((result.directory / "eventos.jsonl").read_bytes(), self.events)
        self.assertEqual((result.directory / "errores.txt").read_bytes(), self.errors)
        self.assertEqual((result.directory / "respuesta.md").read_text(), self.answer)
        self.assertIn(json.dumps(question, ensure_ascii=False), (result.directory / "entrada.txt").read_text())
        metadata = self.metadata(result)
        self.assertEqual(metadata["estado"], "completada")
        self.assertEqual(metadata["codigo_salida"], 0)
        self.assertIsNone(metadata["motivo_fallo"])
        self.assertEqual(metadata["documentos_disponibles"], [f"docs/{name}" for name in agent.DOCUMENTS])
        self.assertIsNone(metadata["documentos_consultados"])
        self.assertGreaterEqual(metadata["duracion_segundos"], 0)
        self.assertIn("fecha_inicio_utc", metadata)
        self.assertTrue(all(not path.exists() for path in self.workspaces))
        self.process.assert_called_once()

    def test_empty_question_is_rejected_before_creating_a_run(self):
        for question in ("", " \t\n"):
            with self.subTest(question=question), redirect_stderr(io.StringIO()) as output:
                with self.assertRaises(SystemExit) as error:
                    agent.main([question])
                self.assertEqual(error.exception.code, 2)
                self.assertIn("vacía", output.getvalue())
        self.process.assert_not_called()
        self.assertFalse((self.project / "runs").exists())

    def test_missing_document_prevents_codex_call(self):
        (self.project / "docs" / "git-push.md").unlink()
        result = agent.execute_question("¿Qué hace push?", self.project)
        self.assert_failure(result, "documentacion_incompleta")
        self.assertIn("git-push.md", result.error)
        self.process.assert_not_called()
        self.assertEqual(self.metadata(result)["documentos_disponibles"], [])

    def test_codex_not_installed(self):
        self.process.side_effect = FileNotFoundError("codex")
        result = agent.execute_question("¿Qué hace add?", self.project)
        self.assert_failure(result, "codex_no_instalado")
        self.assertIn("PATH", result.error)
        self.assertEqual(len(list((result.directory / "docs").iterdir())), 5)

    def test_nonzero_exit_keeps_diagnostics_and_partial_answer(self):
        def fail(command, **kwargs):
            self.simulate_success(command, **kwargs)
            return subprocess.CompletedProcess(command, 7)

        self.process.side_effect = fail
        result = agent.execute_question("¿Qué hace add?", self.project)
        self.assert_failure(result, "salida_con_error", code=7)
        self.assertEqual((result.directory / "eventos.jsonl").read_bytes(), self.events)
        self.assertEqual((result.directory / "errores.txt").read_bytes(), self.errors)
        self.assertEqual((result.directory / "respuesta.md").read_text(), self.answer)
        self.assertEqual(result.answer, "")

    def test_timeout_keeps_partial_outputs(self):
        def timeout(command, **kwargs):
            self.simulate_success(command, **kwargs)
            raise subprocess.TimeoutExpired(command, kwargs["timeout"])

        self.process.side_effect = timeout
        result = agent.execute_question("¿Qué hace add?", self.project)
        self.assert_failure(result, "tiempo_agotado")
        self.assertIn("180", result.error)
        self.assertEqual((result.directory / "eventos.jsonl").read_bytes(), self.events)
        self.assertEqual((result.directory / "errores.txt").read_bytes(), self.errors)
        self.assertEqual((result.directory / "respuesta.md").read_text(), self.answer)
        self.assertTrue(all(not path.exists() for path in self.workspaces))

    def test_missing_final_answer(self):
        def no_answer(command, **kwargs):
            result = self.simulate_success(command, **kwargs)
            Path(command[command.index("-o") + 1]).unlink()
            return result

        self.process.side_effect = no_answer
        result = agent.execute_question("¿Qué hace add?", self.project)
        self.assert_failure(result, "respuesta_ausente", code=0)
        self.assertEqual((result.directory / "respuesta.md").read_bytes(), b"")

    def test_empty_final_answer(self):
        self.answer = " \n\t"
        result = agent.execute_question("¿Qué hace add?", self.project)
        self.assert_failure(result, "respuesta_vacia", code=0)

    def test_main_uses_script_location_from_another_directory(self):
        elsewhere = self.base / "elsewhere"
        elsewhere.mkdir()
        with patch.object(agent, "__file__", str(self.project / "git_docs_agent.py")):
            with chdir(elsewhere), redirect_stdout(io.StringIO()) as output:
                self.assertEqual(agent.main(["¿Qué hace add?"]), 0)
        self.assertIn(self.answer, output.getvalue())
        self.assertIn(str(self.project / "runs"), output.getvalue())
        self.assertFalse((elsewhere / "runs").exists())

    def test_main_reports_failure_and_run_location(self):
        self.process.side_effect = FileNotFoundError("codex")
        with patch.object(agent, "__file__", str(self.project / "git_docs_agent.py")):
            with redirect_stderr(io.StringIO()) as output, redirect_stdout(io.StringIO()) as answer:
                self.assertEqual(agent.main(["¿Qué hace add?"]), 1)
        self.assertIn("Error:", output.getvalue())
        self.assertIn(str(self.project / "runs"), output.getvalue())
        self.assertEqual(answer.getvalue(), "")

    def test_runs_have_unique_directories(self):
        first = agent.execute_question("¿Qué hace add?", self.project)
        second = agent.execute_question("¿Qué hace add?", self.project)
        self.assertNotEqual(first.directory, second.directory)
        self.assertTrue(first.directory.exists())
        self.assertTrue(second.directory.exists())

    def test_temporary_directory_stays_outside_project_even_with_custom_tmpdir(self):
        with patch.object(agent.tempfile, "gettempdir", return_value=str(self.project)):
            result = agent.execute_question("¿Qué hace add?", self.project)
        self.assertIsNone(result.error)
        self.assertTrue(all(not path.is_relative_to(self.project) for path in self.workspaces))


if __name__ == "__main__":
    unittest.main()
