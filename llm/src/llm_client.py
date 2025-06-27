#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author : sz
@Project: mini_dev
@File   : llm_client.py
@Time   : 2025/6/9 10:12
"""

from openai import AzureOpenAI, OpenAI
from openai.types.chat import ChatCompletionUserMessageParam


class LLMClient:
    """
    Initialize the LLM client.
    Support OpenAI & Azure.
    """

    def __init__(
        self,
        provider: str,
        model: str,
        api_key: str,
        base_url: str = None,
        api_version: str = None,
        temperature: float = 0,
        max_tokens: int = 512,
        max_retries: int = 10,
        stop=None,
    ):
        if provider == "azure":
            self.client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version or "2024-02-01",
                base_url=base_url,
                max_retries=max_retries,
            )

        else:
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                max_retries=max_retries,
            )

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.stop = stop or ["--", "\n\n", ";", "#"]
        self.is_chat_model = "instruct" not in self.model

    def ask(self, prompt: str) -> str:
        """
        Sends a prompt to the configured LLM and returns the text response.
        """
        if self.is_chat_model:
            messages = [ChatCompletionUserMessageParam(role="user", content=prompt)]
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stop=self.stop,
            )
            result = response.choices[0].message.content

        else: # if model is an Instruct model
            response = self.client.completions.create(
                model=self.model,
                prompt=prompt,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stop=self.stop,
            )
            result = response.choices[0].text

        return result
