from langchain.tools import tool

@tool
def flights_finder(query: str):
    """
    Search flights based on user query.
    """

    # Replace this with Amadeus API
    return """
Flights

Airline: Emirates
Departure: Mumbai
Arrival: Dubai

Price: ₹18,400

Website:
https://www.emirates.com
    """


@tool
def hotels_finder(query: str):
    """
    Search hotels.
    """

    # Replace this with Booking API

    return """
Hotel

Hotel Name:
Atlantis The Palm

Rate:
₹21,000/night

Website:
https://www.booking.com
    """