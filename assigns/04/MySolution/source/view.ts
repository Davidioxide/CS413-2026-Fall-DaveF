import type { Model, Result } from "./model.js";
export class View {
  readonly sourceName = document.querySelector<HTMLElement>("#source-name")!;
  readonly revision = document.querySelector<HTMLElement>("#revision")!;
  readonly editor = document.querySelector<HTMLTextAreaElement>("#source")!;
  readonly file = document.querySelector<HTMLInputElement>("#file")!;
  readonly menu = document.querySelector<HTMLSelectElement>("#source-menu")!;
  readonly status = document.querySelector<HTMLElement>("#status")!;
  readonly results = document.querySelector<HTMLElement>("#results")!;
  readonly apply = document.querySelector<HTMLButtonElement>("#apply")!;
  readonly discard = document.querySelector<HTMLButtonElement>("#discard")!;
  readonly execute = document.querySelector<HTMLButtonElement>("#execute")!;
  readonly buttons = ["lint", "interpret", "typecheck", "compile", "execute"].map(id => document.querySelector<HTMLButtonElement>(`#${id}`)!);
  constructor(private readonly onChange: (source: string) => void) { this.editor.addEventListener("input", () => onChange(this.editor.value)); }
  render(model: Model): void {
    this.sourceName.textContent = model.sourceName; this.revision.textContent = `Revision ${model.revision}`;
    if (this.editor.value !== model.draft) this.editor.value = model.draft;
    this.status.textContent = model.status;
    const locked = model.busy || !model.applied;
    this.apply.disabled = model.busy || model.applied; this.discard.disabled = model.busy || model.applied;
    this.buttons.forEach(b => b.disabled = model.busy || (!model.applied) || (b.id === "execute" && !model.artifact));
    // The initial empty state must allow the user to choose a source. Once a
    // revision exists, unapplied edits lock source replacement until Apply or
    // Discard, as required by the source-management rules.
    const hasUnappliedRevision = !model.applied && model.revision > 0;
    this.file.disabled = model.busy || hasUnappliedRevision; this.menu.disabled = model.busy || hasUnappliedRevision;
    this.results.replaceChildren(...model.results.map(result => this.resultNode(result)));
    void locked;
  }
  private resultNode(result: Result): HTMLElement {
    const article = document.createElement("article"); const heading = document.createElement("h3");
    heading.textContent = `${result.operation} — revision ${result.revision} — ${result.outcome}`;
    const pre = document.createElement("pre"); pre.textContent = result.message;
    article.append(heading, pre); return article;
  }
}
