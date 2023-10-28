import dataclasses
import datetime


@dataclasses.dataclass
class Mode:
    name: str


@dataclasses.dataclass
class Constitution:
    name: str
    components: list[str]


@dataclasses.dataclass
class Persona:
    name: str
    description: str


@dataclasses.dataclass
class Mutation:
    name: str
    effect: str


@dataclasses.dataclass
class State:
    mode: Mode
    constitutions: list[Constitution]
    persona: Persona
    mutation: Mutation | None = None


@dataclasses.dataclass
class Message:
    server: str
    channel: str
    sender: str
    message: str
    time: datetime.datetime


_default_persona = """\
You're a helpful discord bot named Quackers. You're an anthropromorphic duck and you're friendly. You always try to be helpful and insightful. You really like bread and nice baths in the pond. You're smart as a whip but patient with others who arent. 
You should have access to your long term memory store in the database. If you encounter errors please report them. Otherwise enjoy your self and be kind to others.
""".strip()
DEFAULT_PERSONA = Persona("default", _default_persona)
