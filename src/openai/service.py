import openai
from src.config import settings
from src.learn.serializers import ModuleModel, TopicModel

openai.api_key = settings.OPENAI_API_KEY


def create_prompt_text(
    module_number: int,
    module_name: str,
    topic_number: int,
    topic_name: str,
):
    return f"""
Context:
    - You are a lesson planner with a PhD in education and Finance.
    - Modules are like chapters, which contain sub-units called topics.
    - Each topic can have multiple lessons.
    - A lesson is made up of 1 or more sections.
    - Create a lesson for:
    - Module {module_number} - {module_name}"
    - create lesson no. {topic_number}, title: {topic_name}.
Specifications:
 - The lesson content should be divided into 3 to 5 parts called sections.
 - The format for a section is mentioned later.

Content Guidelines:
 1. Each section of a lesson should be no more than 100 words.
 2. A section can have bullet points to reduce token size.
 3. Keep the text concise and to the point.
 4. After the lesson, there should be a short summary of the content.
 5. The summary should be less than 200 words.
 6. Utilize bulet points to reduce size.

Formatting Guidelines:
 - Add line break character \n after each paragraph.
 - Format the output in json as shown below:
 - Field Order:
  - HEADING
  - PARAGRAPH
  - ORDERED_LIST (OPTIONAL)
  - UNORDERED_LIST (OPTIONAL)
 - Do not add numbers to the content, that will be handled by the frontend.
 - ORDERED_LIST has items numbered from 1.
 - UNORDERED_LIST has items without any numbers.

{{ note: this is an example of how a lesson is divided into sections.\n
\"sections\": [\n {{\n \"id\": 1,\n \"content\": [\n {{\n \"type\":
\"HEADING\",\n \"text\": \"...section heading\"\n }},\n {{\n \"type\":
\"PARAGRAPH\",\n \"text\": \"this is a paragraph, using \n for new lines.\"\n
}},\n {{\n \"type\": \"ORDERED_LIST\",\n \"items\": [\n \"an item\",\n
\"another item\" // it can have upto 5 items\n ]\n }},\n {{\n \"type\":
\"UNORDERED_LIST\",\n \"items\": [\n \"an item\",\n \"another item\"\n ]\n
}}\n ]\n }}\n ]\n}}
"""


class OpenAIService:
    def __init__(self) -> None:
        self.MODEL = "gpt-3.5-turbo"

    def create_new_lesson(
        self,
        topic: TopicModel,
        module: ModuleModel,
    ) -> dict:
        prompt: str = create_prompt_text(
            module_number=module.module_number,
            topic_number=topic.id,
            module_name=module.module_name,
            topic_name=topic.title,
        )

        # example without a system message
        response = openai.ChatCompletion.create(
            model=self.MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0,
        )

        output = response["choices"][0]["message"]["content"]
        return output
