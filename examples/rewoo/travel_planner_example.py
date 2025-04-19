#!/usr/bin/env python3

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only

"""
Travel Planner Example using the REWOO agent pattern.

This example demonstrates how to use the REWOO (Reasoning Without Observation) agent pattern
for creating a detailed travel itinerary with separate planning and execution phases.
"""

import os
import logging
import time
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta

from agent_patterns.patterns.rewoo_agent import REWOOAgent
from langchain_openai import ChatOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DestinationInfoTool:
    """Tool that provides information about travel destinations."""
    
    def __init__(self):
        # Mock database of travel destinations
        self.destinations = {
            "paris": {
                "name": "Paris",
                "country": "France",
                "timezone": "Central European Time (CET/CEST)",
                "language": "French",
                "currency": "Euro (€)",
                "best_time_to_visit": "April to June, September to October",
                "popular_attractions": [
                    "Eiffel Tower", "Louvre Museum", "Notre-Dame Cathedral",
                    "Arc de Triomphe", "Seine River Cruise", "Montmartre",
                    "Champs-Élysées", "Sacré-Cœur", "Musée d'Orsay", "Versailles Palace"
                ],
                "local_cuisine": [
                    "Croissants", "Baguettes", "Coq au Vin", "Beef Bourguignon",
                    "Crêpes", "Escargots", "French Onion Soup", "Macarons", "Crème Brûlée"
                ],
                "visa_requirements": "Schengen visa required for many non-EU citizens",
                "travel_tips": [
                    "Learn basic French phrases", 
                    "Be aware of pickpocketing in tourist areas",
                    "Many shops close on Sundays",
                    "Tipping is not required but appreciated (5-10%)"
                ]
            },
            "tokyo": {
                "name": "Tokyo",
                "country": "Japan",
                "timezone": "Japan Standard Time (JST)",
                "language": "Japanese",
                "currency": "Japanese Yen (¥)",
                "best_time_to_visit": "March-April (cherry blossoms), October-November (autumn)",
                "popular_attractions": [
                    "Tokyo Skytree", "Senso-ji Temple", "Meiji Shrine", "Shibuya Crossing",
                    "Shinjuku Gyoen", "Tokyo Disneyland", "Imperial Palace", "Harajuku",
                    "Tsukiji Fish Market", "Akihabara"
                ],
                "local_cuisine": [
                    "Sushi", "Ramen", "Tempura", "Yakitori", "Udon", "Soba",
                    "Okonomiyaki", "Takoyaki", "Wagashi", "Matcha"
                ],
                "visa_requirements": "Tourist visa required for many nationals, 90-day visa-free for others",
                "travel_tips": [
                    "Public transportation is efficient and punctual",
                    "Learn basic Japanese phrases",
                    "Cash is preferred in many places",
                    "Tipping is not customary and may cause confusion"
                ]
            },
            "new york": {
                "name": "New York City",
                "country": "USA",
                "timezone": "Eastern Time (ET)",
                "language": "English",
                "currency": "US Dollar ($)",
                "best_time_to_visit": "April to June, September to early November",
                "popular_attractions": [
                    "Statue of Liberty", "Times Square", "Central Park", "Empire State Building",
                    "Metropolitan Museum of Art", "Brooklyn Bridge", "Broadway Shows",
                    "Fifth Avenue", "One World Trade Center", "High Line"
                ],
                "local_cuisine": [
                    "New York Pizza", "Bagels", "Pastrami Sandwiches", "Cheesecake",
                    "Hot Dogs", "Pretzels", "Food Trucks", "Diverse International Cuisine"
                ],
                "visa_requirements": "ESTA for eligible countries, visa required for others",
                "travel_tips": [
                    "Subway is the fastest way around the city",
                    "Tipping 15-20% is customary for restaurants and services",
                    "Sales tax is added at checkout",
                    "Look both ways when crossing streets"
                ]
            }
        }
    
    def __call__(self, destination: str, **kwargs) -> str:
        """Provide information about a travel destination."""
        logger.info(f"Getting information about: {destination}")
        
        # Find best match in our database
        destination_key = destination.lower()
        for key, info in self.destinations.items():
            if key in destination_key:
                # Format the information
                result = f"# {info['name']}, {info['country']}\n\n"
                result += f"**Timezone:** {info['timezone']}\n"
                result += f"**Language:** {info['language']}\n"
                result += f"**Currency:** {info['currency']}\n"
                result += f"**Best Time to Visit:** {info['best_time_to_visit']}\n\n"
                
                result += "**Popular Attractions:**\n"
                for attraction in info['popular_attractions']:
                    result += f"- {attraction}\n"
                result += "\n"
                
                result += "**Local Cuisine:**\n"
                for food in info['local_cuisine']:
                    result += f"- {food}\n"
                result += "\n"
                
                result += f"**Visa Requirements:** {info['visa_requirements']}\n\n"
                
                result += "**Travel Tips:**\n"
                for tip in info['travel_tips']:
                    result += f"- {tip}\n"
                    
                return result
        
        return f"No detailed information available for {destination}."


class FlightSearchTool:
    """Tool that simulates searching for flights."""
    
    def __call__(self, origin: str, destination: str, date: str, **kwargs) -> str:
        """Search for flights between locations."""
        logger.info(f"Searching flights from {origin} to {destination} on {date}")
        
        try:
            # Parse the date
            travel_date = datetime.strptime(date, "%Y-%m-%d")
            formatted_date = travel_date.strftime("%A, %B %d, %Y")
            
            # Create mock flight information
            flights = []
            
            # Morning flight
            departure_time = "08:30"
            if "tokyo" in destination.lower() or "japan" in destination.lower():
                arrival_time = "22:45"  # Long flight
                duration = "14h 15m"
                price = 1250
                airlines = ["ANA", "Japan Airlines", "United"]
            elif "paris" in destination.lower() or "france" in destination.lower():
                arrival_time = "18:15"  # Medium flight
                duration = "9h 45m"
                price = 950
                airlines = ["Air France", "Delta", "American Airlines"]
            elif "york" in destination.lower() or "nyc" in destination.lower():
                arrival_time = "11:30"  # Short flight
                duration = "3h"
                price = 450
                airlines = ["Delta", "JetBlue", "American Airlines"]
            else:
                arrival_time = "16:30"  # Default
                duration = "8h"
                price = 800
                airlines = ["Various Airlines"]
                
            flights.append({
                "departure_date": formatted_date,
                "departure_time": departure_time,
                "arrival_time": arrival_time,
                "duration": duration,
                "airline": airlines[0],
                "price": f"${price}",
                "stops": "Non-stop"
            })
            
            # Evening flight
            departure_time = "16:45"
            if "tokyo" in destination.lower() or "japan" in destination.lower():
                arrival_time = "07:30+1"  # Long flight, next day
                duration = "14h 45m"
                price = 1150
                airline = airlines[1]
            elif "paris" in destination.lower() or "france" in destination.lower():
                arrival_time = "02:30+1"  # Medium flight, next day
                duration = "9h 45m"
                price = 875
                airline = airlines[1]
            elif "york" in destination.lower() or "nyc" in destination.lower():
                arrival_time = "19:50"  # Short flight
                duration = "3h 5m"
                price = 400
                airline = airlines[1]
            else:
                arrival_time = "00:45+1"  # Default
                duration = "8h"
                price = 750
                airline = airlines[0]
                
            flights.append({
                "departure_date": formatted_date,
                "departure_time": departure_time,
                "arrival_time": arrival_time,
                "duration": duration,
                "airline": airline,
                "price": f"${price}",
                "stops": "Non-stop"
            })
            
            # Format the results
            result = f"Flights from {origin} to {destination} on {formatted_date}:\n\n"
            
            for i, flight in enumerate(flights, 1):
                next_day = "+" in flight["arrival_time"]
                arrival_note = " (Next day)" if next_day else ""
                arrival_time = flight["arrival_time"].replace("+1", "") + arrival_note
                
                result += f"Flight {i}:\n"
                result += f"- Airline: {flight['airline']}\n"
                result += f"- Departure: {flight['departure_time']}\n"
                result += f"- Arrival: {arrival_time}\n"
                result += f"- Duration: {flight['duration']}\n"
                result += f"- Price: {flight['price']}\n"
                result += f"- Stops: {flight['stops']}\n\n"
                
            return result
            
        except Exception as e:
            return f"Error searching for flights: {str(e)}. Please ensure date format is YYYY-MM-DD."


class HotelSearchTool:
    """Tool that simulates searching for hotels."""
    
    def __call__(self, location: str, check_in: str, check_out: str, **kwargs) -> str:
        """Search for hotels at a location."""
        logger.info(f"Searching hotels in {location} from {check_in} to {check_out}")
        
        try:
            # Parse dates
            check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
            check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
            
            # Calculate stay duration
            stay_days = (check_out_date - check_in_date).days
            
            if stay_days <= 0:
                return "Error: Check-out date must be after check-in date."
                
            # Create mock hotel list based on location
            hotels = []
            
            if "tokyo" in location.lower() or "japan" in location.lower():
                hotels = [
                    {
                        "name": "Tokyo Luxury Hotel",
                        "rating": 5,
                        "price_per_night": 350,
                        "location": "Shinjuku, Tokyo",
                        "amenities": ["Free Wi-Fi", "Pool", "Spa", "Restaurant", "Fitness Center"],
                        "description": "Luxury hotel in the heart of Shinjuku with stunning city views."
                    },
                    {
                        "name": "Tokyo Business Hotel",
                        "rating": 4,
                        "price_per_night": 200,
                        "location": "Shibuya, Tokyo",
                        "amenities": ["Free Wi-Fi", "Restaurant", "Business Center"],
                        "description": "Convenient and comfortable hotel near Shibuya Crossing."
                    },
                    {
                        "name": "Tokyo Budget Inn",
                        "rating": 3,
                        "price_per_night": 120,
                        "location": "Asakusa, Tokyo",
                        "amenities": ["Free Wi-Fi", "Shared Kitchen"],
                        "description": "Affordable accommodations near historic Asakusa district."
                    }
                ]
            elif "paris" in location.lower() or "france" in location.lower():
                hotels = [
                    {
                        "name": "Paris Elegance Hotel",
                        "rating": 5,
                        "price_per_night": 380,
                        "location": "8th Arrondissement, Paris",
                        "amenities": ["Free Wi-Fi", "Spa", "Restaurant", "Room Service", "Views of Eiffel Tower"],
                        "description": "Elegant 5-star hotel with stunning views of the Eiffel Tower."
                    },
                    {
                        "name": "Le Marais Boutique Hotel",
                        "rating": 4,
                        "price_per_night": 220,
                        "location": "Le Marais, Paris",
                        "amenities": ["Free Wi-Fi", "Breakfast Included", "Airport Shuttle"],
                        "description": "Charming boutique hotel in the historic Le Marais district."
                    },
                    {
                        "name": "Paris Budget Stay",
                        "rating": 3,
                        "price_per_night": 140,
                        "location": "Montmartre, Paris",
                        "amenities": ["Free Wi-Fi", "Breakfast Available"],
                        "description": "Comfortable budget accommodations in artistic Montmartre."
                    }
                ]
            elif "york" in location.lower() or "nyc" in location.lower():
                hotels = [
                    {
                        "name": "Manhattan Luxury Suites",
                        "rating": 5,
                        "price_per_night": 420,
                        "location": "Midtown Manhattan, New York",
                        "amenities": ["Free Wi-Fi", "Pool", "Spa", "Restaurant", "Fitness Center", "Central Park Views"],
                        "description": "Luxury hotel in the heart of Manhattan with Central Park views."
                    },
                    {
                        "name": "Brooklyn Heights Hotel",
                        "rating": 4,
                        "price_per_night": 250,
                        "location": "Brooklyn Heights, New York",
                        "amenities": ["Free Wi-Fi", "Restaurant", "Fitness Center", "Rooftop Bar"],
                        "description": "Modern hotel in Brooklyn with Manhattan skyline views."
                    },
                    {
                        "name": "Queens Budget Hotel",
                        "rating": 3,
                        "price_per_night": 150,
                        "location": "Queens, New York",
                        "amenities": ["Free Wi-Fi", "Breakfast Available", "Parking"],
                        "description": "Affordable hotel with convenient access to Manhattan."
                    }
                ]
            else:
                hotels = [
                    {
                        "name": "Luxury Hotel",
                        "rating": 5,
                        "price_per_night": 300,
                        "location": f"Downtown, {location}",
                        "amenities": ["Free Wi-Fi", "Pool", "Spa", "Restaurant"],
                        "description": f"Top-rated luxury hotel in {location}."
                    },
                    {
                        "name": "Mid-Range Hotel",
                        "rating": 4,
                        "price_per_night": 180,
                        "location": f"City Center, {location}",
                        "amenities": ["Free Wi-Fi", "Restaurant", "Fitness Center"],
                        "description": f"Comfortable 4-star hotel in {location}."
                    },
                    {
                        "name": "Budget Stay",
                        "rating": 3,
                        "price_per_night": 100,
                        "location": f"Various Locations, {location}",
                        "amenities": ["Free Wi-Fi"],
                        "description": f"Affordable accommodations in {location}."
                    }
                ]
            
            # Format the results
            result = f"Hotels in {location} for {stay_days} nights (Check-in: {check_in}, Check-out: {check_out}):\n\n"
            
            for hotel in hotels:
                total_price = hotel["price_per_night"] * stay_days
                result += f"**{hotel['name']}** - {'⭐' * hotel['rating']}\n"
                result += f"Location: {hotel['location']}\n"
                result += f"Price: ${hotel['price_per_night']} per night (Total: ${total_price} for {stay_days} nights)\n"
                result += f"Amenities: {', '.join(hotel['amenities'])}\n"
                result += f"Description: {hotel['description']}\n\n"
                
            return result
            
        except Exception as e:
            return f"Error searching for hotels: {str(e)}. Please ensure date format is YYYY-MM-DD."


class AttractionSearchTool:
    """Tool that provides information about attractions."""
    
    def __init__(self):
        # Mock database of attractions
        self.attractions = {
            "eiffel tower": {
                "name": "Eiffel Tower",
                "location": "Paris, France",
                "description": "Iconic wrought-iron lattice tower on the Champ de Mars. It's one of the world's most recognizable landmarks.",
                "opening_hours": "9:00 AM - 12:45 AM (last elevator ascent at 11:00 PM)",
                "price": "€26.80 for adults to the summit",
                "tips": [
                    "Book tickets online in advance to avoid long lines",
                    "Visit during sunset for spectacular views",
                    "The first and second floors are accessible by stairs"
                ]
            },
            "louvre": {
                "name": "Louvre Museum",
                "location": "Paris, France",
                "description": "The world's largest art museum and a historic monument. Home to thousands of works of art including the Mona Lisa.",
                "opening_hours": "9:00 AM - 6:00 PM, Closed on Tuesdays",
                "price": "€17 for adults",
                "tips": [
                    "Plan your visit in advance as the museum is huge",
                    "The Mona Lisa often has the biggest crowds",
                    "Consider getting the Paris Museum Pass if visiting multiple museums"
                ]
            },
            "tokyo skytree": {
                "name": "Tokyo Skytree",
                "location": "Tokyo, Japan",
                "description": "A broadcasting and observation tower, and the tallest structure in Japan.",
                "opening_hours": "10:00 AM - 10:00 PM",
                "price": "¥3,100 for adults to the main observatory",
                "tips": [
                    "Visit on clear days for the best views",
                    "Book tickets in advance during tourist season",
                    "The lower floors have excellent shopping and dining options"
                ]
            },
            "senso-ji": {
                "name": "Senso-ji Temple",
                "location": "Asakusa, Tokyo, Japan",
                "description": "Tokyo's oldest temple, dedicated to the Buddhist goddess of mercy, Kannon.",
                "opening_hours": "Temple grounds are open 24/7, Main hall: 6:00 AM - 5:00 PM",
                "price": "Free admission to the temple grounds",
                "tips": [
                    "Visit early morning or evening to avoid crowds",
                    "Try traditional food from vendors along Nakamise Street",
                    "Don't miss the large red lantern at the Kaminarimon Gate"
                ]
            },
            "statue of liberty": {
                "name": "Statue of Liberty",
                "location": "Liberty Island, New York, USA",
                "description": "Iconic copper statue that represents freedom and democracy, gifted by France to America.",
                "opening_hours": "9:00 AM - 5:00 PM",
                "price": "$25.50 for adults (includes ferry and access to pedestal)",
                "tips": [
                    "Book crown access months in advance if desired",
                    "Security screening is required before boarding the ferry",
                    "Combine with a visit to Ellis Island Immigration Museum"
                ]
            },
            "central park": {
                "name": "Central Park",
                "location": "Manhattan, New York, USA",
                "description": "An 843-acre urban park that serves as a respite from the city's buildings and traffic.",
                "opening_hours": "6:00 AM - 1:00 AM",
                "price": "Free admission",
                "tips": [
                    "Rent bikes to explore the park efficiently",
                    "Visit the Bethesda Fountain and Bow Bridge for iconic photo spots",
                    "The Metropolitan Museum of Art is located on the east side of the park"
                ]
            }
        }
    
    def __call__(self, attraction: str, **kwargs) -> str:
        """Provide information about an attraction."""
        logger.info(f"Getting information about attraction: {attraction}")
        
        # Find best match in our database
        attraction_key = attraction.lower()
        for key, info in self.attractions.items():
            if key in attraction_key:
                # Format the information
                result = f"# {info['name']}\n"
                result += f"**Location:** {info['location']}\n\n"
                result += f"**Description:** {info['description']}\n\n"
                result += f"**Opening Hours:** {info['opening_hours']}\n"
                result += f"**Admission:** {info['price']}\n\n"
                
                result += "**Visitor Tips:**\n"
                for tip in info['tips']:
                    result += f"- {tip}\n"
                    
                return result
        
        return f"No detailed information available for {attraction}."


def main():
    """Run the example."""
    # Get API key from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    # Get model configurations from environment
    planner_provider = os.environ.get("WORKER_MODEL_PROVIDER", "openai")
    planner_model = os.environ.get("WORKER_MODEL_NAME", "gpt-4o")
    solver_provider = os.environ.get("SOLVER_MODEL_PROVIDER", "openai")
    solver_model = os.environ.get("SOLVER_MODEL_NAME", "gpt-4o")
    
    if not api_key and not anthropic_api_key:
        logger.warning("Neither OPENAI_API_KEY nor ANTHROPIC_API_KEY set. Using mock mode.")
        # Create mock implementation
        from unittest.mock import MagicMock
        
        # Create a mock LLM that gives pre-scripted responses
        mock_responses = {
            "planning": """
Step 1: Research Paris as a travel destination
Use the destination info tool to gather general information about Paris.

Step 2: Find flights to Paris
Search for flight options from New York to Paris for the specified dates.

Step 3: Find accommodation in Paris
Search for hotel options in Paris for the specified dates.

Step 4: Research top attractions in Paris
Get information about key attractions like the Eiffel Tower and Louvre Museum.

Step 5: Create a 3-day itinerary
Create a day-by-day itinerary that covers the key attractions while allowing time for exploration.

Step 6: Provide travel tips and recommendations
Add specific recommendations for transportation, dining, and cultural experiences.

Step 7: Compile the comprehensive travel plan
Combine all gathered information into a complete travel plan document.
            """,
            "execution1": """
I'll start by researching Paris as a travel destination.

TOOL: destination_info
destination: Paris
            """,
            "execution2": """
Now I'll search for flights from New York to Paris for the specified dates.

TOOL: flight_search
origin: New York
destination: Paris
date: 2023-09-15
            """,
            "execution3": """
Let's find accommodation options in Paris for the duration of the trip.

TOOL: hotel_search
location: Paris
check_in: 2023-09-15
check_out: 2023-09-18
            """,
            "execution4": """
Now I'll research key attractions in Paris, starting with the Eiffel Tower.

TOOL: attraction_search
attraction: Eiffel Tower
            """,
            "execution5": """
Let's also get information about the Louvre Museum, another iconic Paris attraction.

TOOL: attraction_search
attraction: Louvre
            """,
            "final": """
# Comprehensive Travel Plan: New York to Paris
**September 15-18, 2023**

## Destination Overview
Paris, known as the "City of Light," is the capital of France and one of the world's most visited destinations. The city is known for its art, culture, cuisine, and historic landmarks.

**Currency:** Euro (€)  
**Language:** French  
**Timezone:** Central European Time (CET)  
**Best time to visit:** April-June and September-October (you're traveling during an ideal time!)

## Travel Details

### Flight
**Departure:** New York to Paris  
**Date:** Friday, September 15, 2023  
**Recommended Flight:** Morning departure (8:30 AM)  
**Airline:** Air France  
**Arrival:** 18:15 (local time)  
**Duration:** 9h 45m  
**Price Estimate:** $950 per person

### Accommodation
**Recommended Hotel:** Le Marais Boutique Hotel  
**Location:** Le Marais district (central location with great access to attractions)  
**Rating:** ⭐⭐⭐⭐  
**Price:** $220 per night ($660 total for 3 nights)  
**Amenities:** Free Wi-Fi, Breakfast Included, Airport Shuttle  
**Description:** Charming boutique hotel in the historic Le Marais district.

## 3-Day Itinerary

### Day 1 (September 15)
- **Morning:** Arrival and hotel check-in
- **Afternoon:** Light exploration of Le Marais neighborhood
- **Evening:** Dinner at a local bistro and early night (to recover from jet lag)

### Day 2 (September 16)
- **Morning:** Visit the Eiffel Tower (book tickets in advance for 9:00 AM to avoid crowds)
- **Afternoon:** Cruise on the Seine River
- **Evening:** Dinner in the Latin Quarter

### Day 3 (September 17)
- **Morning:** Visit the Louvre Museum (arrive early, plan to see key works like the Mona Lisa)
- **Afternoon:** Explore Montmartre and visit Sacré-Cœur
- **Evening:** Farewell dinner in a traditional French restaurant

### Day 4 (September 18)
- **Morning:** Final sightseeing or shopping
- **Afternoon:** Departure for New York

## Key Attractions

### Eiffel Tower
- **Opening Hours:** 9:00 AM - 12:45 AM
- **Admission:** €26.80 for adults to the summit
- **Tips:** 
  - Book tickets online in advance
  - Visit during sunset for spectacular views
  - Consider taking the stairs to the first level to avoid long elevator lines

### Louvre Museum
- **Opening Hours:** 9:00 AM - 6:00 PM (Closed on Tuesdays)
- **Admission:** €17 for adults
- **Tips:**
  - Plan your visit in advance as the museum is huge
  - The Mona Lisa often has the biggest crowds
  - Consider getting the Paris Museum Pass if visiting multiple museums

## Travel Tips

### Transportation
- The Paris Metro is efficient and affordable for getting around
- Consider purchasing a Paris Visite pass for unlimited public transportation
- Taxi or shuttle service is recommended from Charles de Gaulle Airport to your hotel

### Dining
- Breakfast is typically light (croissant and coffee)
- Lunch is between 12-2 PM, dinner typically starts at 7:30 PM or later
- Make reservations for dinner at popular restaurants
- Try classic French dishes: Coq au Vin, Beef Bourguignon, Crêpes, Escargots, and French pastries

### Cultural Tips
- Learn basic French phrases (bonjour, merci, s'il vous plaît)
- Dress smartly, especially when dining out
- Be aware of pickpocketing in tourist areas
- Many shops close on Sundays
- Tipping is not required but appreciated (5-10%)

## Estimated Budget
- Flights: $950
- Accommodation: $660
- Meals: $300-400
- Attractions: $200
- Transportation: $100
- Miscellaneous: $200
- **Total estimate:** $2,410-$2,510

Enjoy your trip to Paris! This beautiful city has something for everyone, from world-class art and architecture to incredible food and charming streets perfect for wandering.
            """
        }
        
        class MockLLM:
            def __init__(self, responses):
                self.responses = responses
                self.call_count = 0
                
            def invoke(self, messages):
                self.call_count += 1
                message_str = str(messages)
                
                if "planning" in message_str.lower() or "plan" in message_str.lower():
                    return mock_responses["planning"]
                elif "step" in message_str.lower() and "execution" in message_str.lower():
                    # Return different responses based on the step number
                    step_mention = message_str.lower().find("step")
                    if step_mention >= 0:
                        for i in range(1, 6):
                            if f"step {i}" in message_str.lower():
                                return mock_responses.get(f"execution{i}", mock_responses["execution1"])
                    
                    # Default execution response if step number not found
                    return mock_responses["execution1"]
                elif "final" in message_str.lower() or "synthesize" in message_str.lower():
                    return mock_responses["final"]
                    
                return "Default response based on: " + str(messages)
        
        # Create mock LLMs
        planner_llm = MockLLM(mock_responses)
        solver_llm = MockLLM(mock_responses)
    else:
        # Create LLMs based on provider
        if planner_provider.lower() == "openai":
            planner_llm = ChatOpenAI(
                model=planner_model,
                temperature=0.7,
                api_key=api_key
            )
        elif planner_provider.lower() == "anthropic":
            from langchain_anthropic import ChatAnthropic
            planner_llm = ChatAnthropic(
                model=planner_model,
                temperature=0.7,
                api_key=anthropic_api_key
            )
        else:
            logger.warning(f"Unsupported planner provider: {planner_provider}. Falling back to OpenAI.")
            planner_llm = ChatOpenAI(
                model=planner_model,
                temperature=0.7,
                api_key=api_key
            )
        
        if solver_provider.lower() == "openai":
            solver_llm = ChatOpenAI(
                model=solver_model,
                temperature=0.2,
                api_key=api_key
            )
        elif solver_provider.lower() == "anthropic":
            from langchain_anthropic import ChatAnthropic
            solver_llm = ChatAnthropic(
                model=solver_model,
                temperature=0.2,
                api_key=anthropic_api_key
            )
        else:
            logger.warning(f"Unsupported solver provider: {solver_provider}. Falling back to OpenAI.")
            solver_llm = ChatOpenAI(
                model=solver_model,
                temperature=0.2,
                api_key=api_key
            )
    
    # Create tools
    destination_info_tool = DestinationInfoTool()
    flight_search_tool = FlightSearchTool()
    hotel_search_tool = HotelSearchTool()
    attraction_search_tool = AttractionSearchTool()
    
    # Define the prompt directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(script_dir))
    src_prompt_dir = os.path.join(repo_root, "src", "agent_patterns", "prompts", "REWOOAgent")
    prompt_dir = os.path.join(repo_root, "agent_patterns", "prompts", "REWOOAgent")
    
    # Use the src path if it exists, otherwise use the non-src path
    if os.path.exists(src_prompt_dir):
        prompt_dir = src_prompt_dir
    
    # Create REWOO agent
    agent = REWOOAgent(
        llm_configs={
            "planner": planner_llm,
            "solver": solver_llm
        },
        tool_registry={
            "destination_info": destination_info_tool,
            "flight_search": flight_search_tool,
            "hotel_search": hotel_search_tool,
            "attraction_search": attraction_search_tool
        },
        prompt_dir=prompt_dir,
        max_iterations=20  # Increase from default to handle all steps in the plan
    )
    
    # Run the agent
    query = "Create a comprehensive travel plan for a 3-day trip from New York to Paris, including flights, accommodation, and a daily itinerary of attractions to visit. Travel dates: September 15-18, 2023."
    print(f"\nRequest: {query}\n")
    print("-" * 80)
    print("Starting REWOO agent execution...\n")
    
    start_time = time.time()
    # Increase recursion limit to handle the complex plan
    config = {"recursion_limit": 100}
    result = agent.run(query, config=config)
    elapsed_time = time.time() - start_time
    
    print("\nTravel Plan:")
    print("-" * 80)
    print(result)
    print("-" * 80)
    print(f"Execution completed in {elapsed_time:.2f} seconds.")


if __name__ == "__main__":
    main() 