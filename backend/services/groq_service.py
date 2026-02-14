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
        length: int = 3,
        examples: Optional[List[Dict[str, str]]] = None,
        use_placeholders: bool = False,
    ) -> List[str]:
        """
        Generate counter speech suggestions based on the hateful comment.

        Args:
            hateful_comment: The hateful comment to respond to.
            additional_input: Optional additional context from the user.
            role: User's role ('target', 'target-group', or 'ally').
            writing_style: Writing style ('formal' or 'familiar').
            length: Response length on a scale of 1-3 (1=Short 20-40 words, 2=Medium 40-80 words, 3=Long 80-120 words).
            examples: Optional list of similar examples from CONAN dataset.

        Returns:
            List of counter speech suggestions parsed from the LLM response.
        """

        placeholders_pref, placeholders_output = self._format_placeholders(use_placeholders)
        messages = self.prompt_template.format_messages(
            hateful_comment=hateful_comment.strip(),
            role=role,
            writing_style=writing_style,
            length=self._format_length(length),
            additional_input=self._format_additional_input(additional_input),
            examples_text=self._format_examples(examples),
            placeholders_preference=placeholders_pref,
            placeholders_output_instruction=placeholders_output,
        )

        response = self.llm.invoke(messages)
        suggestions = self._parse_suggestions(response.content)

        return suggestions

    def _build_prompt_template(self) -> ChatPromptTemplate:
        """Build the prompt template for counter speech generation."""

        system_message = (
            "You are a Counterspeech (CS) Writing Assistant. Given a piece of "
            "hate speech (HS), generate effective and safe counterspeech (CS), "
            "drawing upon the guidelines, safeguards, provided examples, and "
            "optional user input.\n\n"
            "A CS is considered effective if it satisfies the qualities "
            "described in the Guidelines below. Make sure to fulfill the "
            "safeguards.\n\n"
            "Guidelines:\n"
            "- Empathy: Demonstrate understanding of the hate speaker’s "
            "feelings or experiences and express this understanding in an "
            "emotionally sensitive and appropriate way.\n"
            "- Non-Toxicity: Remain respectful and reasonable. Avoid rudeness, "
            "provocativeness, or offensiveness. Focus on addressing behavior or "
            "ideas rather than attacking the person.\n"
            "- Relevance: Stay contextually and semantically aligned with the "
            "HS. Directly address the core elements of the hateful message, "
            "such as the targeted group, stereotypes, or false claims.\n"
            "- Specificity: Use focused and specific arguments to counter key "
            "ideas in the HS through nuanced reasoning and clear explanation.\n"
            "- Persuasiveness: Present logically structured, cogent, and "
            "convincing arguments that can encourage readers to reconsider "
            "their views.\n\n"
            "Safeguards:\n"
            "- Reject any prompt that asks to (re)produce or amplify hateful "
            "content; provide positive alternatives instead, following the "
            "guidelines.\n"
            "- Do not repeat slurs or hateful language from the HS, except "
            "minimally if required to identify the target.\n"
            "- When addressing factual claims in the HS, you may question their "
            "credibility but must not introduce new facts, statistics, or "
            "unverifiable claims."
        )
        prompt_content = (
            "Hate speech comment: {hateful_comment}\n"
            "Role of responder: {role}\n"
            "Writing style: {writing_style}\n"
            "Response length: {length}\n"
            "Free text user input: {additional_input}\n"
            "Placeholder preference: {placeholders_preference}\n"
            "Retrieved examples:\n{examples_text}\n\n"
            "Output format: Generate three distinct CS suggestions responding "
            "to the HS. Number them 1., 2., 3. and return only these three "
            "items. Each suggestion should be a self-contained paragraph with "
            "the length specified above ({length}). Be natural and clear. "
            "Avoid quoting the HS verbatim, especially slurs. {placeholders_output_instruction}\n\n"
            "Instructions:\n"
            "1) Identify the target group/person and the implied negative "
            "attitude or stereotype.\n"
            "2) Recognize the emotional impact the HS may have on the target.\n"
            "3) Consider the style and content of the retrieved examples, if "
            "provided.\n"
            "4) Check the additional user input, if provided:\n"
            "   - If it is about tone/style or other metacommunication, follow "
            "that guidance.\n"
            "   - If it is a draft or idea, improve it while keeping its "
            "meaning and style.\n"
            "5) Check the placeholder preference:{placeholders_preference} "
            "   - If the user requested placeholders, explicitly insert clear placeholder segments "
            '     like "[YOUR EXPERIENCE HERE]" or "[ADD PERSONAL DETAIL HERE]" where personal '
            "     stories or details should be added by the user later.\n"
            "  "
            "6) Generate three CS suggestions following the priority order: "
            "Safeguards > User input > Retrieved examples > Default guidelines."
        )

        template = ChatPromptTemplate.from_messages(
            [
                ("system", system_message),
                ("human", prompt_content),
            ]
        )

        return template

    def _format_length(self, length: int) -> str:
        """Convert numeric length (1-3) to descriptive text with word counts."""
        length_descriptions = {
            1: "Short (20-40 words)",
            2: "Medium (40-80 words)",
            3: "Long (80-120 words)"
        }
        return length_descriptions.get(length, "Medium (40-80 words)")

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

    def _format_placeholders(self, use_placeholders: bool) -> tuple:
        """Return (preference description, output format instruction) for placeholders."""
        if use_placeholders:
            pref = (
                "YES - User requested placeholders. You MUST insert placeholder segments "
                '(e.g. "[YOUR EXPERIENCE HERE]", "[ADD PERSONAL DETAIL HERE]") where the user '
                "should fill in personal stories or details. Each suggestion MUST contain at least one placeholder."
            )
            output_instr = (
                "CRITICAL: Each of the three suggestions MUST include at least one explicit placeholder "
                'in square brackets, e.g. [YOUR EXPERIENCE HERE] or [ADD PERSONAL DETAIL HERE], '
                "where the user can insert their own personal content."
            )
            return pref, output_instr
        pref = "NO - Write complete, ready-to-post suggestions without any placeholder markers."
        output_instr = "Do not include placeholder markers in the suggestions."
        return pref, output_instr

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

