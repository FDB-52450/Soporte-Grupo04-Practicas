from dataclasses import dataclass, field

@dataclass
class DatosEntrevista:
    nombre_entrevistado: str
    edad_entrevistado: int
    nombre_empresa: str
    puesto: str
    nivel: str

    total_preguntas: int
    temas: list[str]
    pregunta_actual: int = 1
    ultima_pregunta: str = ""
    historial: list[dict[str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.total_preguntas < 1:
            raise ValueError("total_preguntas debe ser mayor que cero")
        if len(self.temas) < self.total_preguntas:
            raise ValueError("Debe existir un tema para cada pregunta")