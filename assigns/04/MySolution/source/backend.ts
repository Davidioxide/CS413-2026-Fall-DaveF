import type { Result, Artifact } from "./model.js";
export interface Backend {
  lint(source: string, revision: number): Promise<Result>;
  interpret(source: string, revision: number): Promise<Result>;
  typecheck(source: string, revision: number): Promise<Result>;
  compile(source: string, revision: number): Promise<Result>;
  execute(artifact: Artifact, revision: number): Promise<Result>;
}
const call = async (operation: string, source: string, revision: number): Promise<Result> => {
  const response = await fetch("/api/operation", { method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ operation, source, revision }) });
  if (!response.ok) throw new Error(`Backend HTTP error ${response.status}`);
  return await response.json() as Result;
};
export class HttpBackend implements Backend {
  lint = (s: string, r: number) => call("lint", s, r);
  interpret = (s: string, r: number) => call("interpret", s, r);
  typecheck = (s: string, r: number) => call("typecheck", s, r);
  compile = (s: string, r: number) => call("compile", s, r);
  execute = async (_a: Artifact, r: number) => call("execute", "", r);
}
