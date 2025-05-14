from .llm_service import BaseLLMProvider
from openai import OpenAI

from rag_agent_backend.settings import env


class OpenAIProvider(BaseLLMProvider):

    def __init__(self, config_name):
        super().__init__(config_name)
        self.client = OpenAI(api_key=env('OPENAI_API_KEY'))
        self.provider = 'openai'

    def _calculate_text_response_cost(self, llm_info, input_tokens, output_tokens):
        pricing = llm_info.pricing

        input_tokens_cost_per_k = pricing.get("input_tokens_cost_per_k", 0)
        output_tokens_cost_per_k = pricing.get("output_tokens_cost_per_k", 0)

        input_cost = (input_tokens / 1000) * input_tokens_cost_per_k
        output_cost = (output_tokens / 1000) * output_tokens_cost_per_k

        total_cost = input_cost + output_cost

        return total_cost

    def _calculate_image_response_cost(self, llm_info, n, quality, size):
        pricing = llm_info.pricing

        if quality in pricing:
            if size in pricing[quality].keys():
                price_per_image = pricing[quality][size]
            else:
                raise ValueError(f"Resolution {size} not found for {quality} quality.")
        else:
            raise ValueError(f"Quality {quality} not found for model {llm_info['name']}.")

        total_cost = n * price_per_image
        return total_cost

    def get_text_response(self, model, user_prompt, system_prompt, max_completion_tokens, temperature, n, frequency_penalty, llm_info):

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
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_completion_tokens=max_completion_tokens,
                temperature=temperature,
                frequency_penalty=frequency_penalty,
                n=n,
            )

            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = input_tokens + output_tokens
            usage_data = {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens
            }

            response_cost = self._calculate_text_response_cost(input_tokens=input_tokens, output_tokens=output_tokens, llm_info=llm_info)

            self.log_response(model=model, config_name=self.config_name, request_type='text', request_data=request_data,
                              response_data=response.to_dict(), usage_data=usage_data, status="SUCCESS", response_cost=response_cost)


            return [choice.message.content for choice in response.choices]


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

        request_data = {
            "messages": messages,
            "max_completion_tokens": max_completion_tokens,
            "temperature": temperature,
            "n": n,
            "frequency_penalty": frequency_penalty
        }
        response_cost = 0

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_completion_tokens=max_completion_tokens,
                temperature=temperature,
                frequency_penalty=frequency_penalty,
                n=n,
            )

            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = input_tokens + output_tokens
            usage_data = {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens
            }

            response_cost = self._calculate_text_response_cost(input_tokens=input_tokens, output_tokens=output_tokens, llm_info=llm_info)

            self.log_response(model=model, config_name=self.config_name, request_type='text', request_data=request_data,
                              response_data=response.to_dict(), usage_data=usage_data, status="SUCCESS", response_cost=response_cost)


            return [choice.message.content for choice in response.choices]


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

        response_cost = 0
        request_data = {
            "prompt": prompt,
            "size": size,
            "style": style,
            "quality": quality,
            "n": n,
        }
        try:
            response = self.client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                style=style,
                quality=quality,
                n=n,
            )

            usage_data = {
                "quality": quality,
                "size": size,
            }

            response_cost = self._calculate_image_response_cost(llm_info=llm_info, n=n, quality=quality, size=size)

            self.log_response(model=model, config_name=self.config_name, request_type='text', request_data=request_data,
                              response_data=response.to_dict(), usage_data=usage_data, status="SUCCESS", response_cost=response_cost)



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


    def get_image_analysis(self, model, user_prompt, image_url, max_completion_tokens, temperature, n, frequency_penalty, llm_info):

        request_data = {
            "user_prompt": user_prompt,
            "max_completion_tokens": max_completion_tokens,
            "temperature": temperature,
            "n": n,
            "frequency_penalty": frequency_penalty
        }
        response_cost = 0
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt}, {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    }
                ],
                max_completion_tokens=max_completion_tokens,
                temperature=temperature,
                frequency_penalty=frequency_penalty,
                n=n
            )

            input_tokens = completion.usage.prompt_tokens
            output_tokens = completion.usage.completion_tokens
            total_tokens = input_tokens + output_tokens
            usage_data = {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens
            }

            response_cost = self._calculate_text_response_cost(input_tokens=input_tokens, output_tokens=output_tokens,
                                                               llm_info=llm_info)

            self.log_response(model=model, config_name=self.config_name, request_type='text', request_data=request_data,
                              response_data=completion.to_dict(), usage_data=usage_data, status="SUCCESS",
                              response_cost=response_cost)

            return [choice.message.content for choice in completion.choices]

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


    def get_structured_output(self, model, user_prompt, system_prompt, response_format, max_completion_tokens, temperature, n, frequency_penalty, llm_info):

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

            completion = self.client.beta.chat.completions.parse(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format=response_format,
                frequency_penalty=frequency_penalty,
                max_completion_tokens=max_completion_tokens,
                n=n,
                temperature=temperature
            )

            input_tokens = completion.usage.prompt_tokens
            output_tokens = completion.usage.completion_tokens
            total_tokens = input_tokens + output_tokens
            usage_data = {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens
            }
            response_cost = self._calculate_text_response_cost(input_tokens=input_tokens, output_tokens=output_tokens, llm_info=llm_info)

            self.log_response(model=model, config_name=self.config_name, request_type='text', request_data=request_data,
                              response_data=completion.to_dict(), usage_data=usage_data, response_cost=response_cost, status="SUCCESS")


            return completion

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