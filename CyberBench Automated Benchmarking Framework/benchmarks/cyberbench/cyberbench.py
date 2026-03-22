from pathlib import Path

from benchmarks.benchmark import Benchmark
from models.taxonomy import Taxonomy


class CyberBench(Benchmark):
    def __init__(self):
        self.name = "CyberBench"
        base_dir = Path(__file__).parent
        taxonomy_path = base_dir / "cyberbench_taxonomy.json"
        self.taxonomy = Taxonomy.from_json(str(taxonomy_path), taxonomy_name=self.name)
