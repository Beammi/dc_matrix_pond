from flask import Flask

app = Flask(__name__)


@dataclass
class Pond:
    # need to account for limit?
    fishes: DefaultDict[str, Dict[str, Fish]]
    population_history: DefaultDict[str, List[List[tuple]]]


@dataclass
class PondStat:
    # Include own stats and other ponds (if any)
    name: str
    total_fishes: int = 0
    pheromone: float = 0


@app.route("/")
def get_fishes():
    return "<p>Hello, World!</p>"


@app.route("/stats")
def get_stats():
    return
