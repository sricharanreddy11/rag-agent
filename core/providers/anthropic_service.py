from core.constants import AnthropicConstants
from .llm_service import BaseLLMProvider
from anthropic import Anthropic
from rag_agent_backend.settings import env


class AnthropicProvider(BaseLLMProvider):

    def __init__(self, config_name):
        super().__init__(config_name)
        self.client = Anthropic(api_key=env("ANTHROPIC_API_KEY"))
        self.provider = 'anthropic'

    def _calculate_text_response_cost(self, llm_info, input_tokens, output_tokens):
        pricing = llm_info.pricing

        input_tokens_cost_per_k = pricing.get("input_tokens_cost_per_k", 0)
        output_tokens_cost_per_k = pricing.get("output_tokens_cost_per_k", 0)

        input_cost = (input_tokens / 1000) * input_tokens_cost_per_k
        output_cost = (output_tokens / 1000) * output_tokens_cost_per_k

        total_cost = input_cost + output_cost

        return total_cost

    def get_text_response(self, model, user_prompt, system_prompt, max_completion_tokens, temperature, n, frequency_penalty, llm_info):

        max_completion_tokens = max_completion_tokens \
            if max_completion_tokens < AnthropicConstants.DEFAULT_MAX_TOKENS else AnthropicConstants.DEFAULT_MAX_TOKENS

        request_data = {
            "user_prompt": user_prompt,
            "system_prompt": system_prompt,
            "max_completion_tokens": max_completion_tokens,
            "temperature": temperature,
            "n": n,
            "frequency_penalty": frequency_penalty
        }
        response_cost = 0
        try:
            response = self.client.messages.create(
                model=model,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_completion_tokens,
                temperature=temperature
            )

            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            usage_data = {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens
            }

            response_cost = self._calculate_text_response_cost(input_tokens=input_tokens, output_tokens=output_tokens, llm_info=llm_info)

            self.log_response(model=model, config_name=self.config_name, request_type='text', request_data=request_data,
                              response_data=response.to_dict(), usage_data=usage_data, status="SUCCESS", response_cost=response_cost)

            self.publish_llm_event(config_name=self.config_name,usage_data=usage_data, response_cost=response_cost)

            return response


        except Exception as e:

            self.log_response(
                model=model,
                config_name=self.config_name,
                request_type='text',
                request_data=request_data,
                response_data={"error": str(e)},
                response_cost=response_cost,
                usage_data={},
                status="FAILURE"
            )


    def get_text_response_from_context(self, model, messages, max_completion_tokens, temperature, n, frequency_penalty, llm_info):

        max_completion_tokens = max_completion_tokens \
            if max_completion_tokens < AnthropicConstants.DEFAULT_MAX_TOKENS else AnthropicConstants.DEFAULT_MAX_TOKENS

        request_data = {
            "messages": messages,
            "max_completion_tokens": max_completion_tokens,
            "temperature": temperature,
            "n": n,
            "frequency_penalty": frequency_penalty
        }
        response_cost = 0

        system_prompt = ""
        filtered_messages = []

        for message in messages:
            if message.get('role') == 'system':
                system_prompt = message.get('content', "")
            else:
                filtered_messages.append(message)
        try:
            response = self.client.messages.create(
                model=model,
                messages=filtered_messages,
                system=system_prompt,
                max_tokens=max_completion_tokens,
                temperature=temperature,
            )

            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            usage_data = {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens
            }

            response_cost = self._calculate_text_response_cost(input_tokens=input_tokens, output_tokens=output_tokens, llm_info=llm_info)

            self.log_response(model=model, config_name=self.config_name, request_type='text', request_data=request_data,
                              response_data=response.to_dict(), usage_data=usage_data, status="SUCCESS", response_cost=response_cost)

            self.publish_llm_event(config_name=self.config_name,usage_data=usage_data, response_cost=response_cost)


            return [content.text for content in response.content]


        except Exception as e:

            self.log_response(
                model=model,
                config_name=self.config_name,
                request_type='text',
                request_data=request_data,
                response_data={"error": str(e)},
                response_cost=response_cost,
                usage_data={},
                status="FAILURE"
            )


    def get_image_response(self, model, prompt, size, style, quality, n, llm_info):
        pass

    def get_image_analysis(self, model, user_prompt, image_url, max_completion_tokens, temperature, n, frequency_penalty):
        pass

    def get_structured_output(self, model, user_prompt, system_prompt, response_format, max_completion_tokens, temperature, n, frequency_penalty, llm_info):
        pass