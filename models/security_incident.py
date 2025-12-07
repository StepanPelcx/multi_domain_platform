class SecurityIncident:
    """Represents a cybersecurity incident in the platform."""

    #creating variables of the class
    def __init__(self, incident_id: int, incident_type: str, severity: str, status: str, description: str):
        self.__id = incident_id
        self.__incident_type = incident_type
        self.__severity = severity
        self.__status = status
        self.__description = description

    def get_id(self) -> str:
        """Returns id of the incident."""
        return self.__id
    
    def get_severity(self) -> str:
        """Returns severity of the incident."""
        return self.__severity
    
    def get_status(self) -> str:
        """Returns status of the incident."""
        return self.__status
    
    def get_description(self) -> str:
        """Returns description of the incident."""
        return self.__description
    
    def update_status(self, new_status: str) -> None:
        """Updates status of the incident."""
        self.__status = new_status

    def get_severity_level(self) -> int:
        """Return an integer severity level."""
        mapping = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
        }
        return mapping.get(self.__severity.lower(), 0)
    
    #self description
    def __str__(self) -> str:
        return f"Incident {self.__id} [{self.__severity.upper()}] {self.__incident_type}"
    
    