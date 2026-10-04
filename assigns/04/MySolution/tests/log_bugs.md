# Bug log

## Initial source controls were disabled

- **Bug:** On first page load, `Load source` and `Choose File` were disabled. They became usable only after pressing `Discard changes`, even though no source had been loaded and there were no edits to discard.
- **Reason:** `View.render()` disabled both controls whenever `model.applied` was false. The model starts with `applied = false`, so the initial empty state was incorrectly treated as an unapplied-edit state. The initial Discard button was also disabled, leaving no normal way to unlock the controls.
- **Fix:** Added a `hasUnappliedRevision` check in `source/view.ts`: source replacement is disabled only when `!model.applied && model.revision > 0`. Revision zero now remains interactive so users can choose a file, select a canned source, or begin manual input. Once a source revision exists with unapplied edits, the replacement lock still applies until Apply or Discard.
