class ITTicket:
    """Represents an IT Tickets in the platform"""

    #creating variables of the class
    def __init__(self, ticket_id: int, title: str, priority: str, status: str, assighned_to: str):
        self.__id = ticket_id
        self.__title = title
        self.__priority = priority
        self.__status = status
        self.__assigned_to = assighned_to

    def assign_to(self, staff: str) -> None:
        """Assigns self to a staff."""
        self.__assigned_to = staff

    def close_ticket(self) -> None:
        """Sets status of a ticket to close"""
        self.__status = "Closed"

    def get_status(self) -> str:
        """Returns a status of the ticket"""
        return self.__status
    
    #self description
    def __str__(self) -> str:
        return(
            f"Ticket {self.__id}: {self.__title} "
            f"[{self.__priority}] - {self.__status} (assigned to: {self.__assigned_to})"
        )