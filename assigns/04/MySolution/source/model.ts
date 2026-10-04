export type Outcome = "success" | "invalid_input" | "language_error" | "runtime_error" | "backend_error" | "timeout" | "not_implemented";
export type Result = { operation: string; revision: number; outcome: Outcome; message: string; freeVariables?: string[] };
export type Artifact = { revision: number; id: string; description: string };

export class Model {
  source = ""; sourceName = "No source loaded"; revision = 0; applied = false;
  draft = ""; results: Result[] = []; artifact: Artifact | null = null;
  busy = false; status = "Ready.";

  acceptSource(source: string, name: string): void {
    if (!source.trim()) throw new Error("Source must not be empty or whitespace-only.");
    if (new TextEncoder().encode(source).length > 65536) throw new Error("Source exceeds the 65536-byte limit.");
    this.source = source; this.draft = source; this.sourceName = name; this.revision += 1;
    this.applied = true; this.results = []; this.artifact = null;
  }
  setDraft(draft: string): void { this.draft = draft; this.applied = draft === this.source; }
  applyDraft(): void { this.acceptSource(this.draft, this.sourceName); }
  discardDraft(): void { this.draft = this.source; this.applied = true; }
  addResult(result: Result): void { if (result.revision === this.revision) this.results.unshift(result); }
}
