import { Model } from "./model.js";
import { View } from "./view.js";
import { Controller } from "./controller.js";
import { HttpBackend } from "./backend.js";
const model = new Model();
const view = new View(source => { model.setDraft(source); view.render(model); });
new Controller(model, view, new HttpBackend());
