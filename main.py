import discord
import openai
import re
import requests
import io
from dotenv import load_dotenv
import os

# Load .env file 
load_dotenv()
openai_key= os.environ.get('OPENAI')
channel_id = os.environ.get('CHANNELID')
secret_token = os.environ.get('TOKEN')

client = discord.Client(intents=discord.Intents.all())
openai.api_key = openai_key

@client.event
async def on_member_join(member):
    channel = client.get_channel(channel_id)
    await channel.send(
    "Hi there! Welcome to NAME's server. Here are the available commands:\n"
    "!image: ChatGPT to generate an image from your prompt.\n"
    "!chat: ChatGPT will answer your prompts.\n"
    "!code: ChatGPT will put the answer in a code box.\n"
    "!creative: ChatGPT will answer your prompts with more variety and creativtiy (look up ChatGPT temperature settings, it is set to 1 with this command and 0.5 for the other).\n"
    "!creativecode: ChatGPT will answer your prompt with both !creative and !code."
    )

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith("!help"):
        response = "Here are the available commands:\n"
        response += "!image: Generate an image from your prompt.\n"
        response += "!chat: Answers prompts.\n"
        response += "!code: Answers prompts and puts the answer in a code box (for easy copy and pasting).\n"
        response += "!creative: Answers prompts with more variety and creativity (look up ChatGPT temperature settings, it is set to 1 with this command and 0.5 for the other).\n"
        response += "!creativecode: Answers prompts with both !creative and !code.\n"
        await message.channel.send(response)

    elif message.content.startswith("!image"):
        prompt = message.content[7:]
        loading_message = await message.channel.send("***Generating image, please wait...***")
        api_url = "https://api.openai.com/v1/images/generations"
        api_key = {"Authorization": f"Bearer {openai.api_key}"}
        data = {"model": "image-alpha-001", "prompt": prompt, "num_images": 1, "size": "512x512", "response_format": "url"}
        response = requests.post(api_url, headers=api_key, json=data).json()
        if 'error' in response:
            error_message = response['error']['message']
            await message.channel.send(f"An error occurred: {error_message}")
        else:
            image_url = response['data'][0]['url']
            response = requests.get(image_url)
            image = response.content
            await message.channel.send(file=discord.File(io.BytesIO(image), 'image.jpg'))
        await loading_message.delete()

    elif message.content.startswith("!code"):
        prompt = message.content[6:]
        loading_message = await message.channel.send("***Generating response, please wait...***")
        response_lines = generate_response(prompt, 0.5)
        if isinstance(response_lines, str):
            await message.channel.send(response_lines)
        else:
            response = '\n'.join(response_lines)
            await message.channel.send('```' + response + '```')
        await loading_message.delete()

    elif message.content.startswith("!creative"):
        prompt = message.content[10:]
        loading_message = await message.channel.send("***Generating response, please wait...***")
        response_lines = generate_response(prompt, 1)
        if isinstance(response_lines, str):
            await message.channel.send(response_lines)
        else:
            for line in response_lines:
                await message.channel.send(line)
        await loading_message.delete()

    elif message.content.startswith("!creativecode"):
        prompt = message.content[4:]
        loading_message = await message.channel.send("***Generating response, please wait...***")
        response_lines = generate_response(prompt, 1)
        if isinstance(response_lines, str):
            await message.channel.send(response_lines)
        else:
            response = '\n'.join(response_lines)
            await message.channel.send('```' + response + '```')
        await loading_message.delete()

    elif message.content.startswith("!chat"):
        prompt = message.content[6:]  
        loading_message = await message.channel.send("***Generating response, please wait...***")
        response_lines = generate_response(prompt, 0.5)
        if isinstance(response_lines, str):
            await message.channel.send(response_lines)
        else:
            for line in response_lines:
                await message.channel.send(line)
        await loading_message.delete()

def generate_response(prompt, temperature):
    completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=2048, # 4000 is the maximum number of tokens for the davinci 003 GPT3 model
        n=1,
        stop=None,
        temperature=temperature,
    )

    if 'error' in completions:
        return completions['error']['message']
    else:
        message = completions.choices[0].text
    if '!code' in prompt:
        return message
    elif '!creativecode' in prompt:
        return message
    elif '!image' in prompt:
        return message
    else:
        words = re.split(r'\b', message)
        lines = []
        current_line = ''
        for word in words:
            if len(current_line + word) > 75:
                lines.append(current_line)
                current_line = ''
            current_line += word
        lines.append(current_line)
        return lines

client.run(secret_token)


