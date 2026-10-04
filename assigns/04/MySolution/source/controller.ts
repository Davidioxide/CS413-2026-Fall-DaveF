import { Model } from "./model.js";
import type { Backend } from "./backend.js";
import { View } from "./view.js";
const examples: Record<string, [string, string]> = {
  factorial: ["factorial.lambda", 'D0Eapp(D0Efix("fac", "n", D0Eif0(D0Eop2("==", D0Evar("n"), D0Eint(0)), D0Eint(1), D0Eop2("*", D0Evar("n"), D0Eapp(D0Evar("fac"), D0Eop2("-", D0Evar("n"), D0Eint(1)))))), D0Eint(5))'],
  fibonacci: ["fibonacci.lambda", 'D0Eapp(D0Efix("fib", "n", D0Eif0(D0Eop2("<=", D0Evar("n"), D0Eint(1)), D0Evar("n"), D0Eop2("+", D0Eapp(D0Evar("fib"), D0Eop2("-", D0Evar("n"), D0Eint(1))), D0Eapp(D0Evar("fib"), D0Eop2("-", D0Evar("n"), D0Eint(2)))))), D0Eint(8))']
};
export class Controller {
  constructor(private readonly model: Model, private readonly view: View, private readonly backend: Backend) { this.bind(); this.view.render(model); }
  private bind(): void {
    this.view.menu.addEventListener("change", () => { const choice = this.view.menu.value; if (choice === "manual") { this.model.draft = ""; this.model.applied = false; this.model.sourceName = "Manual input"; this.model.status = "Enter source, then apply it."; this.view.render(this.model); } else if (examples[choice]) this.replace(...examples[choice]); this.view.menu.value = ""; });
    this.view.file.addEventListener("change", async () => { const file = this.view.file.files?.[0]; if (!file) return; try { const bytes = await file.arrayBuffer(); const source = new TextDecoder("utf-8", { fatal: true }).decode(bytes); this.replace(file.name, source); } catch (e) { this.fail(new Error("File is not valid UTF-8.")); this.view.render(this.model); } this.view.file.value = ""; });
    this.view.apply.addEventListener("click", () => { try { this.model.applyDraft(); this.model.status = "Changes applied."; } catch (e) { this.fail(e); } this.view.render(this.model); });
    this.view.discard.addEventListener("click", () => { this.model.discardDraft(); this.model.status = "Unapplied changes discarded."; this.view.render(this.model); });
    this.view.buttons.forEach(button => button.addEventListener("click", () => void this.run(button.id)));
  }
  private replace(name: string, source: string): void { try { this.model.acceptSource(source, name); this.model.status = "Source loaded. Apply edits before operating."; } catch (e) { this.fail(e); } this.view.render(this.model); }
  private async run(operation: string): Promise<void> {
    this.model.busy = true; this.model.status = `Running ${operation}…`; this.view.render(this.model); const revision = this.model.revision;
    try { const result = operation === "lint" ? await this.backend.lint(this.model.source, revision) : operation === "interpret" ? await this.backend.interpret(this.model.source, revision) : operation === "typecheck" ? await this.backend.typecheck(this.model.source, revision) : operation === "compile" ? await this.backend.compile(this.model.source, revision) : await this.backend.execute(this.model.artifact!, revision); this.model.addResult(result); this.model.status = `${operation} finished.`; }
    catch (e) { this.model.addResult({ operation, revision, outcome: "backend_error", message: String(e) }); this.model.status = `${operation} failed; you can retry.`; }
    finally { this.model.busy = false; this.view.render(this.model); }
  }
  private fail(error: unknown): void { this.model.status = `Source rejected: ${error instanceof Error ? error.message : String(error)}`; }
}
