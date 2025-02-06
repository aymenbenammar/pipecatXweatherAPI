import os
import sys
import asyncio
import aiohttp
from dotenv import load_dotenv
from loguru import logger
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.deepgram import DeepgramSTTService, DeepgramTTSService
from pipecat.services.groq import GroqLLMService
from pipecat.transports.services.daily import DailyParams, DailyTransport
from pipecat_flows import  FlowConfig, FlowManager
from weather_flow import get_weather
from runner import configure


load_dotenv(override=True)
logger.remove(0)
logger.add(sys.stderr, level="DEBUG")



flow_config: FlowConfig = {
    "initial_node": "greeting",
    "nodes": {
        "greeting": {
            "role_messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant capable of discussing various topics and providing weather information. Your responses will be converted to audio, so avoid special characters."
                }
            ],
            "task_messages": [
                {
                    "role": "system",
                    "content": "Greet the user and ask how you can help them today."
                }
            ],
            "functions": [
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "handler": get_weather,
                        "description": "Get weather for a specific city",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "city": {"type": "string", "description": "City name"}
                            },
                            "required": ["city"]
                        },
                    }
                }
            ],
            "transition_to": "conversation"
        },
        "conversation": {
            "task_messages": [
                {
                    "role": "system",
                    "content": "Engage in conversation with the user. If they ask about weather, use the get_weather function. Otherwise, respond appropriately to their queries or statements."
                }
            ],
            "functions": [
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "handler": get_weather,
                        "description": "Get weather for a specific city",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "city": {"type": "string", "description": "City name"}
                            },
                            "required": ["city"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "end_conversation",
                        "description": "End the conversation",
                        "parameters": {"type": "object", "properties": {}},
                        "transition_to": "end"
                    }
                }
            ]
        }
    }
}

async def main():
    async with aiohttp.ClientSession() as session:
        (room_url, _) = await configure(session)

        transport = DailyTransport(
            room_url,
            None,
            "Weather Bot",
            DailyParams(
                audio_out_enabled=True,
                vad_enabled=True,
                vad_analyzer=SileroVADAnalyzer(),
                vad_audio_passthrough=True,
            ),
        )

        stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
        tts= DeepgramTTSService(api_key=os.getenv("DEEPGRAM_API_KEY"),voice="aura-helios-en")
        llm = GroqLLMService(
            api_key=os.getenv("GROQ_API_KEY"), model="llama-3.3-70b-versatile"
        )
        context = OpenAILLMContext()
        context_aggregator = llm.create_context_aggregator(context)

        pipeline = Pipeline(
            [
                transport.input(), 
                stt,  
                context_aggregator.user(),  
                llm,  
                tts,  
                transport.output(),  
                context_aggregator.assistant(),  
            ]
        )

        task = PipelineTask(pipeline, PipelineParams(allow_interruptions=True))

        flow_manager = FlowManager(
            task=task,
            llm=llm,
            context_aggregator=context_aggregator,
            flow_config=flow_config,
        )

        @transport.event_handler("on_first_participant_joined")
        async def on_first_participant_joined(transport, participant):
            await transport.capture_participant_transcription(participant["id"])
            await flow_manager.initialize()

        runner = PipelineRunner()
        await runner.run(task)
    flow_manager = FlowManager(flow_config)
    while True:
        user_input = input("User: ")
        result = await flow_manager.process(user_input)
        print(f"Assistant: {result.content}")
        if result.node == "end":
            break

if __name__ == "__main__":
    asyncio.run(main())
