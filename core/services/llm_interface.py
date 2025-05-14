from core.constants import OpenAIConstants
from core.models import LLMConfiguration
from core.providers.anthropic_service import AnthropicProvider
from core.providers.llm_service import BaseLLMProvider
from core.providers.openai_service import OpenAIProvider


class LLMInterface(object):

    def __init__(self):
        self.providers = {
            'openai': OpenAIProvider,
            'anthropic': AnthropicProvider
        }

    def get_llm_provider(self, provider_name: str, config_name) -> BaseLLMProvider:
        """
        Retrieve a language model (LLM) provider based on the given provider name and configuration.

        :param provider_name: str - The name of the LLM provider to retrieve.
        :param config_name: Any - The configuration to initialize the provider with.
        :return: BaseLLMProvider - An instance of the requested LLM provider.
        :raises ValueError: If the specified provider is not present in the available providers.
        """

        # status, message = check_event_permission_for_tenant(event_name=CRMEventConstants.ANALYTICS)
        # if not status:
        #     raise PaymentRequiredError(message)

        provider = self.providers.get(provider_name)
        if not provider:
            raise ValueError(f"Provider '{provider_name}' is not present.")

        return provider(config_name)

    def get_config_object(self, config_name):
        """
        Retrieve a configuration object based on the given configuration name.

        :param config_name: str - The name of the configuration to retrieve.
        :return: LLMConfiguration - The configuration object corresponding to the given name.
        :raises ValueError: If the specified configuration is not present.
        """
        config_obj = LLMConfiguration.objects.filter(config_name=config_name).first()
        if not config_obj:
            raise ValueError(f"Config {config_name} is not present")

        return config_obj

    def get_custom_response(
            self,
            user_prompt,
            config_name,
            model=None,
            system_prompt=None,
            max_completion_tokens=None,
            temperature=None,
            n=None,
            frequency_penalty=None
    ):
        """
        Generate a custom response from an LLM provider based on the provided user prompt and configuration.

        :param user_prompt: str - The prompt or query provided by the user.
        :param config_name: str - The name of the configuration to use for generating the response.
        :param model: str, optional - The model to be used for the response. Defaults to the model specified in the configuration.
        :param system_prompt: str, optional - The system's behavior prompt. Defaults to the system behavior in the configuration.
        :param max_completion_tokens: int, optional - The maximum number of tokens in the completion. Defaults to the value in the configuration or a predefined default.
        :param temperature: float, optional - The randomness of the model's responses. Defaults to the value in the configuration or a predefined low temperature.
        :param n: int, optional - The number of responses to generate. Defaults to the response count specified in the configuration.
        :param frequency_penalty: float, optional - A penalty for using repetitive words. Defaults to the value in the configuration or a predefined default.
        :return: str - The content of the first choice in the generated response.
        :raises ValueError: If the specified configuration or provider is not present.
        """

        config_obj = self.get_config_object(config_name)
        llm_provider = self.get_llm_provider(config_obj.llm_provider, config_name)

        config_data = config_obj.config_data
        llm_info = config_obj.llm_info

        response = llm_provider.get_text_response(
            model=model or config_obj.model,
            user_prompt=user_prompt,
            system_prompt=system_prompt or config_obj.system_behaviour,
            max_completion_tokens=max_completion_tokens or config_data.get("max_completion_tokens", OpenAIConstants.DEFAULT_MAX_COMPLETION_TOKENS),
            temperature=temperature if temperature is not None else config_data.get("temperature", OpenAIConstants.LOW_TEMPERATURE),
            n=n or config_obj.response_count,
            frequency_penalty=frequency_penalty if frequency_penalty is not None else config_data.get("frequency_penalty", OpenAIConstants.DEFAULT_FREQUENCY_PENALTY),
            llm_info=llm_info
        )

        return response[0]

    def get_custom_response_from_context(
            self,
            messages,
            config_name,
            model=None,
            max_completion_tokens=None,
            temperature=None,
            n=None,
            frequency_penalty=None
    ):
        """
        Generate a custom response from an LLM provider using a conversational context.

        :param messages: list - A list of message dictionaries representing the conversation history (including previous exchanges).
        :param config_name: str - The name of the configuration to use for generating the response.
        :param model: str, optional - The model to be used for the response. Defaults to the model specified in the configuration.
        :param max_completion_tokens: int, optional - The maximum number of tokens in the completion. Defaults to the value in the configuration or a predefined default.
        :param temperature: float, optional - The randomness of the model's responses. Defaults to the value in the configuration or a predefined low temperature.
        :param n: int, optional - The number of responses to generate. Defaults to the response count specified in the configuration.
        :param frequency_penalty: float, optional - A penalty for using repetitive words. Defaults to the value in the configuration or a predefined default.
        :return: str - The content of the first choice in the generated response.
        :raises ValueError: If the specified configuration or provider is not present.
        """

        config_obj = self.get_config_object(config_name)
        llm_provider = self.get_llm_provider(config_obj.llm_provider, config_name)


        config_data = config_obj.config_data
        llm_info = config_obj.llm_info

        response = llm_provider.get_text_response_from_context(
            model=model or config_obj.model,
            messages=messages,
            max_completion_tokens=max_completion_tokens or config_data.get("max_completion_tokens", OpenAIConstants.DEFAULT_MAX_COMPLETION_TOKENS),
            temperature=temperature if temperature is not None else config_data.get("temperature", OpenAIConstants.LOW_TEMPERATURE),
            n=n or config_obj.response_count,
            frequency_penalty=frequency_penalty if frequency_penalty is not None else config_data.get("frequency_penalty", OpenAIConstants.DEFAULT_FREQUENCY_PENALTY),
            llm_info=llm_info
        )

        return response[0]

    def get_custom_structured_response(
            self,
            config_name,
            user_prompt,
            response_format,
            model=None,
            system_prompt=None,
            max_completion_tokens=None,
            temperature=None,
            n=None,
            frequency_penalty=None
    ):
        """
        Generate a custom structured response from an LLM provider based on the provided user prompt, configuration, and response format.

        :param config_name: str - The name of the configuration to use for generating the response.
        :param user_prompt: str - The prompt or query provided by the user.
        :param response_format: str - The desired format of the structured response (e.g., JSON, Markdown).
        :param model: str, optional - The model to be used for the response. Defaults to the model specified in the configuration.
        :param system_prompt: str, optional - The system's behavior prompt. Defaults to the system behavior in the configuration.
        :param max_completion_tokens: int, optional - The maximum number of tokens in the completion. Defaults to the value in the configuration or a predefined default.
        :param temperature: float, optional - The randomness of the model's responses. Defaults to the value in the configuration or a predefined low temperature.
        :param n: int, optional - The number of responses to generate. Defaults to the response count specified in the configuration.
        :param frequency_penalty: float, optional - A penalty for using repetitive words. Defaults to the value in the configuration or a predefined default.
        :return: Any - The structured response generated by the LLM provider.
        :raises ValueError: If the specified configuration or provider is not present.
        """

        config_obj = self.get_config_object(config_name)
        llm_provider = self.get_llm_provider(config_obj.llm_provider, config_name)

        config_data = config_obj.config_data
        model = model or config_obj.model
        llm_info = config_obj.llm_info


        response = llm_provider.get_structured_output(
            model=model,
            user_prompt=user_prompt,
            response_format=response_format,
            system_prompt=system_prompt or config_obj.system_behaviour,
            max_completion_tokens=max_completion_tokens or config_data.get("max_completion_tokens", OpenAIConstants.DEFAULT_MAX_COMPLETION_TOKENS),
            temperature=temperature if temperature is not None else config_data.get("temperature", OpenAIConstants.LOW_TEMPERATURE),
            n=n or config_obj.response_count,
            frequency_penalty=frequency_penalty if frequency_penalty is not None else config_data.get(
                "frequency_penalty", OpenAIConstants.DEFAULT_FREQUENCY_PENALTY),
            llm_info=llm_info
        )

        return response