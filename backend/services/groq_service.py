# Groq API service for LLM integration

from typing import Dict, List, Optional

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from config import GROQ_API_KEY, GROQ_MODEL


class GroqService:
    """Service for interacting with Groq API via LangChain."""

    def __init__(self):
        """Initialize the Groq chat model and prompt template."""
        self.llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name=GROQ_MODEL,
            temperature=0.7,
        )
        self.prompt_template = self._build_prompt_template()

    def generate_counter_speech(
        self,
        hateful_comment: str,
        additional_input: Optional[str] = None,
        role: str = "ally",
        writing_style: str = "formal",
        examples: Optional[List[Dict[str, str]]] = None,
    ) -> List[str]:
        """
        Generate counter speech suggestions based on the hateful comment.

        Args:
            hateful_comment: The hateful comment to respond to.
            additional_input: Optional additional context from the user.
            role: User's role ('target', 'target-group', or 'ally').
            writing_style: Writing style ('formal' or 'familiar').
            examples: Optional list of similar examples from CONAN dataset.

        Returns:
            List of counter speech suggestions parsed from the LLM response.
        """

        messages = self.prompt_template.format_messages(
            hateful_comment=hateful_comment.strip(),
            role=role,
            writing_style=writing_style,
            additional_input=self._format_additional_input(additional_input),
            examples_text=self._format_examples(examples),
        )

        response = self.llm.invoke(messages)
        suggestions = self._parse_suggestions(response.content)

        return suggestions

    def _build_prompt_template(self) -> ChatPromptTemplate:
        """Build the prompt template for counter speech generation."""

        system_message = (
            "You are a counterspeech coach helping users respond to hateful content "
            "with empathetic, educational, and de-escalating messages."
        )
        prompt_content = (
            "Hate speech comment:\n{hateful_comment}\n\n"
            "Role of responder: {role}\n\n"
            "Writing style: {writing_style}\n\n"
            "Additional user context:\n{additional_input}\n\n"
            "Relevant reference examples:\n{examples_text}\n\n"
            "Instructions:\n"
            "1. Produce exactly three distinct counter speech suggestions.\n"
            "2. Make them authentic to the specified role and grounded in the examples when helpful.\n"
            "3. Use a {writing_style} writing style (formal = professional, structured, respectful; familiar = conversational, casual, friendly).\n"
            "4. Promote empathy, facts, and constructive dialogue.\n"
            "5. Return them as numbered lines (1., 2., 3.)."
        )

        template = ChatPromptTemplate.from_messages(
            [
                ("system", system_message),
                ("human", prompt_content),
            ]
        )

        return template

    def _format_additional_input(self, additional_input: Optional[str]) -> str:
        """Ensure additional input has a fallback string."""
        if additional_input and additional_input.strip():
            return additional_input.strip()
        return "No additional context provided."

    def _format_examples(
        self, examples: Optional[List[Dict[str, str]]]
    ) -> str:
        """Format retrieved CONAN examples for the prompt."""
        if not examples:
            return "No similar examples found."

        formatted_blocks = []
        for idx, example in enumerate(examples, start=1):
            block = (
                f"Example {idx}:\n"
                f"Hate speech: {example.get('hate_speech', '').strip()}\n"
                f"Counter narrative: {example.get('counter_narrative', '').strip()}\n"
                f"Target: {example.get('target', 'N/A')}\n"
            )
            formatted_blocks.append(block.strip())

        return "\n\n".join(formatted_blocks)

    def _parse_suggestions(self, response_text: str) -> List[str]:
        """Parse the LLM response to extract exactly three suggestions."""
        lines = response_text.strip().split("\n")
        suggestions: List[str] = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            clean_line = line
            for prefix in ["1.", "2.", "3.", "-", "*"]:
                if clean_line.startswith(prefix):
                    clean_line = clean_line[len(prefix) :].strip()
                    break

            if clean_line:
                suggestions.append(clean_line)

        if len(suggestions) < 3:
            paragraphs = [p.strip() for p in response_text.split("\n\n") if p.strip()]
            for paragraph in paragraphs:
                if paragraph not in suggestions:
                    suggestions.append(paragraph)
                if len(suggestions) == 3:
                    break

        while len(suggestions) < 3:
            suggestions.append("Please try generating again.")

        return suggestions[:3]

