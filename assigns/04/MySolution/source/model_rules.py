class ModelRules:
    def __init__(self): self.source = ""; self.source_name = ""; self.revision = 0; self.results = []; self.artifact = None
    def accept(self, source, name):
        if not source.strip(): raise ValueError("empty source")
        if len(source.encode()) > 65536: raise ValueError("source too large")
        self.source, self.source_name = source, name; self.revision += 1; self.results = []; self.artifact = None
