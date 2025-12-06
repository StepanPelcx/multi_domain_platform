class ITTicket:
    def __init__(self, ticket_id: int, title: str, priority: str, status: str, assighned_to: str):
        self.__id = ticket_id
        self.__title = title
        self.__priority = priority
        self.__status = status
        self.__assigned_to = assighned_to

    def assign_to(self, staff: str) -> None:
        self.__assigned_to = staff

    def close_ticket(self) -> None:
        self.__status = "Closed"

    def get_status(self) -> str:
        return self.__status
    
    def __str__(self) -> str:
        return(
            f"Ticket {self.__id}: {self.__title} "
            f"[{self.__priority}] - {self.__status} (assigned to: {self.__assigned_to})"
        )