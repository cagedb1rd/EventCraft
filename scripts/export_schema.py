from pathlib import Path

from eventcraft.schema import Event
from eventcraft.security import write_json

if __name__ == "__main__":
    write_json(Path(__file__).resolve().parents[1] / "assets/event.schema.json", Event.model_json_schema())
