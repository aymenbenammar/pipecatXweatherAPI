# Weather Chatbot

This project implements an AI-powered chatbot capable of engaging in general conversation and providing weather information for specified cities.

## Installation

pip install -r requirements.txt  
NOTE: If you use windows system you will need to use WSL since the library daily-python is not yet avaialable in Windows

## Setup API Keys
Add the Api Keys in the .env file  

DAILY_API_KEY=  
DAILY_SAMPLE_ROOM_URL=  
You can get it from https://www.daily.co/  
Generate API key and create a room   

GROQ_API_KEY=  
You can get it from https://console.groq.com/playground  

DEEPGRAM_API_KEY=  
You can get it from https://console.deepgram.com/  

OPENWEATHER_API_KEY=  
You can get it from https://openweathermap.org/api  


## Project Documentation

### Components

main.py : Define flow config and define LLM to use  
weather_flow.py : Define functions to handle specific weather requests  

### Evolutions 

To add a new flow you need to define it in the flow config  
Then add a new file containing the functions to handle this flow

### Flow Configuration

The chatbot uses a configured flow with two main nodes:
- **greeting**: Initiates the conversation.
- **conversation**: Handles ongoing dialogue, including weather queries.

### LLM Integration

The Language Model (LLM) is integrated to:
- Understand user inputs
- Decide when to fetch weather data
- Generate human-like responses
- Maintain conversation context

### API Integration

OpenWeatherMap API is used to fetch real-time weather data for specified cities.

### Conversation Handling

The chatbot maintains a conversation history to provide context-aware responses. It can engage in general conversation and seamlessly integrate weather information when requested.



## Future Improvements

- Implement more sophisticated error handling
- Add support for multiple languages
- Expand to include more weather-related functionalities (e.g., forecasts, historical data)



