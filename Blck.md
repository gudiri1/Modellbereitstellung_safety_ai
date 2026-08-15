classDiagram
    class Gesamtsystem {
        +Lokales_Steuergerat
        +Remote_Infrastruktur
    }
    class Lokales_Steuergerat {
        <<Subsystem HW>>
        +Sensoren
        +Python_Runtime
        +Physisches_Relais
    }
    class Python_Runtime {
        <<Subsystem SW>>
        +SafetyCriticalClient
        +Pydantic_Validators
    }
    class Remote_Infrastruktur {
        <<Subsystem Cloud>>
        +API_Gateway
        +KI_Modell_vLLM
    }
    Gesamtsystem *-- Lokales_Steuergerat
    Gesamtsystem *-- Remote_Infrastruktur
    Lokales_Steuergerat *-- Python_Runtime
    Remote_Infrastruktur *-- KI_Modell_vLLM
