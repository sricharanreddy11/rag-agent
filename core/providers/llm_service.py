from abc import ABC, abstractmethod

from authenticator.thread_container import ThreadContainer
from core.models import LLMRequestLog


class BaseLLMProvider(ABC):

    def __init__(self, config_name):
        self.config_name = config_name

    @abstractmethod
    def get_text_response(self, **kwargs):
        pass

    @abstractmethod
    def get_text_response_from_context(self, **kwargs):
        pass

    @abstractmethod
    def get_image_response(self, **kwargs):
        pass

    @abstractmethod
    def get_image_analysis(self, **kwargs):
        pass

    @abstractmethod
    def get_structured_output(self, **kwargs):
        pass

    def log_response(self, model, config_name, request_type, request_data, response_data, response_cost, usage_data, status):
        """
        Log the response data of an LLM request for tracking and analysis.

        :param model: str - The model used for the request.
        :param config_name: str - The name of the configuration used.
        :param request_type: str - The type of the request (e.g., 'text', 'image').
        :param request_data: dict - The data sent in the request.
        :param response_data: dict - The data received in the response.
        :param response_cost: float - The cost associated with the response.
        :param usage_data: dict - The token usage data, including input and output tokens.
        :param status: str - The status of the request (e.g., 'success', 'failure').
        :return: None - This method does not return a value.
        :raises Exception: If there is an error while logging the response.
        """

        user_id = ThreadContainer.get_current_user_id()
        LLMRequestLog.objects.create(
            request_model=model,
            config_name = config_name,
            request_type = request_type,
            request_data = request_data,
            response_data = response_data,
            input_tokens = usage_data.get("input_tokens", 0),
            output_tokens = usage_data.get("output_tokens", 0),
            response_cost=response_cost,
            user_id = user_id,
            status = status,
        )


