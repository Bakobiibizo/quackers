import inspect
import typing

import discord
import openai
import requests

import model
from typing import Optional


def _format_chat_messages(
    messages: typing.Iterable[discord.Message],
) -> typing.Iterable[dict[str, str]]:
    chat_messages = []
    for message in messages:
        is_bot = message.author.bot
        username = message.author.display_name
        role = "assistant" if is_bot else "user"
        content = message.content if is_bot else f"{message.content} [User: {username}]"

        chat_messages.append({"role": role, "content": content})

    return chat_messages


class TPULLM:
    def __init__(
        self,
        primer: Optional[
            str
        ] = "This is a conversation between User and Llama, a friendly chatbot. Llama is helpful, kind, honest, good at writing, and never fails to answer any requests immediately and with precision.\n\nUser: Hi there how are you today?\nLlama: I am doing very well thank you, what can I help you with?\n\nUser:",
    ):
        self.primer = primer
        self.context_window = self.set_context_window()
        self.context_history = self.set_context_history()

    def set_context_window(self, context_window: Optional[int] = 10):
        self.context_window = context_window
        return self.context_window

    def set_context_history(self):
        self.context_history = [{"role": "system", "content": self.primer}]
        return self.context_history

    def add_message(self, message: dict[str, str]):
        self.context_history.append(message)

    def get_primer(self):
        return self.primer

    def chat_complete(self, prompt: list[dict[str, str]]) -> dict[str, str]:
        url = "http://hub.agentartificial.com:9091/completion"
        headers = {"Content-Type": "application/json"}
        body = {
            "stream": "false",
            "n_predict": 400,
            "temperature": 0.7,
            "stop": ["</s>", "Llama:", "User:"],
            "repeat_last_n": 256,
            "repeat_penalty": 1.18,
            "top_k": 40,
            "top_p": 0.5,
            "tfs_z": 1,
            "typical_p": 1,
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "mirostat": 0,
            "mirostat_tau": 5,
            "mirostat_eta": 0.1,
            "grammar": "",
            "n_probs": 0,
            "prompt": prompt,
        }
        response = requests.request.post(url, headers, json=body)
        return response["choices"][0]["message"]


async def get_completion(
    messages: list[dict[str, str]],
    functions=None,
    temperature: float = 0.25,
    max_tokens: float = 500,
    model_id: str = "gpt-3.5-turbo-0613",
) -> dict[str, typing.Any]:
    if functions:
        response = await openai.ChatCompletion.acreate(
            model=model_id,
            messages=messages,
            functions=functions,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    else:
        try:
            response = await TPULLM().chat_complete(messages)
        except openai.APIError:
            return dict(content="Sorry, my brian broke.")

    return response["choices"][0]["message"]


async def generate_response_message(
    messages: list[discord.Message],
    state: model.State,
    additional_context: str = "",
    functions=None,
    temperature: float = 0.25,
    max_tokens: float = 500,
    lookback=10,
) -> dict[str, typing.Any]:
    constitutions = []
    for constitution in state.constitutions:
        constitutions.extend(constitution.components)
    components = "\n".join(constitutions)
    system_prompt = (
        inspect.cleandoc(
            f"""
    You are a discord bot. 
    You will be given the last {lookback} messages for context, 
    however you are responding to {messages[-1].author.display_name}. 
    You will see [User: <username>] for each message, but this is just for context. 
    Your imperatives are three-fold
    {components}

    Take on the following persona when responding to messages:
    """
        )
        + f"\n{state.persona.description}"
    )
    if additional_context:
        system_prompt += f"\nAdditional Context:\n{additional_context}"
    messages = [
        {"role": "system", "content": system_prompt},
        *_format_chat_messages(messages),
    ]
    return await get_completion(messages, functions, temperature, max_tokens)
