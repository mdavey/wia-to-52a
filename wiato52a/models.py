from dataclasses import dataclass


@dataclass
class Section:
    band: str
    mode: str
    region: str


@dataclass
class Repeater:
    output_mhz: float
    input_mhz: float
    call: str
    mnemonic: str
    location: str
    service_area: str
    latitude: str
    longitude: str
    status: str
    erp: str
    hasl: str
    timeout: str
    sponsor: str
    tone: str
    notes: str
    section: Section
