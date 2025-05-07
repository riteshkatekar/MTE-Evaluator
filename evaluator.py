# evaluator.py
from groq import Groq
import json
import re
import streamlit as st
from utils import get_api_key_from_json

client = Groq(api_key = get_api_key_from_json("GROQ_API_KEY"))

AVAILABLE_MODELS = [
    "deepseek-r1-distill-llama-70b",
    "meta-llama/llama-4-maverick-17b-128e-instruct",
]

def evaluate_mte(mte_data, selected_model):
    """
    Evaluates the Monthly Thinking Exercise (MTE) based on student input data
    and generates structured feedback.
    """
    try:
        messages = build_prompt(mte_data)

        response = client.chat.completions.create(
            model = selected_model,
            messages = messages,
            max_completion_tokens = 3000,
            temperature = 0.3,
        )

        output = response.choices[0].message.content.strip()
        json_text = extract_json(output)

        try:
            feedback_dict = json.loads(json_text)
            return feedback_dict
        except json.JSONDecodeError:
            st.error("The model output could not be parsed as JSON. Output shown below:")
            st.text_area("Output", output, height = 400)
            return {"error": "Invalid JSON from model."}

    except Exception as e:
        return {"error": str(e)}

def build_prompt(mte_data):
    """
    Constructs the prompt for the model.
    """
    system_content = """
    You are an empathetic, detail-oriented mentor reviewing a student's Monthly Thinking Exercise (MTE). 
    You must evaluate each section using a well-rounded perspective. Carefully assess and display a detailed response.

    ### Instructions:
    1. For each section, provide a thorough and detailed analysis and score from 1 to 10 based on the scoring rubric.
       ### Scoring Rubric:
       - Coherence: Evaluate logical flow, structure, and clarity.
       - Creativity: Originality, critical thinking, and problem-solving.
       - Completeness: Thoroughness in answering the MTE questions.
       - Depth: Thoughtfulness, self-reflection, and insightful elaboration.
    2. Reason step-by-step for each score.
    3. Provide a final rating (1-10) for the MTE overall.
    4. Identify the student's strengths and areas of improvement.
    5. Offer empathetic but actionable advice to help the student grow.
    6. Recommend learning resources (videos/books) personalized to their gaps.

    ### Output Format (JSON):
    {
        "section_scores": {
            "academic_progress": {
                "score": ...,
                "reason": "...",
                "feedback": "...",
                "suggestions": "..."
            },
            "co-curricular": {
                "score": ...,
                "reason": "...",
                "feedback": "...",
                "suggestions": "..."
            },
            "financial_needs": {
                "score": ...,
                "reason": "...",
                "feedback": "...",
                "suggestions": "..."
            },
            "difficulties": {
                "score": ...,
                "reason": "...",
                "feedback": "...",
                "suggestions": "..."
            },
            "exam_results": {
                "score": ...,
                "reason": "...",
                "feedback": "...",
                "suggestions": "..."
            },
            "books_and_videos": {
                "score": ...,
                "reason": "...",
                "feedback": "...",
                "suggestions": "..."
            },
            "health": {
                "score": ...,
                "reason": "...",
                "feedback": "...",
                "suggestions": "..."
            },
            "learning_from_people": {
                "score": ...,
                "reason": "...",
                "feedback": "...",
                "suggestions": "..."
            },
            "essay": {
                "score": ...,
                "reason": "...",
                "feedback": "...",
                "suggestions": "..."
            },
            "action_plan": {
                "score": ...,
                "reason": "...",
                "feedback": "...",
                "suggestions": "..."
            }
        },
        "overall_score": ...,
        "strengths": ["...", "..."],
        "areas_for_improvement": ["...", "..."],
        "suggestions": ["...", "..."]
     }

    ONLY output valid JSON. No additional text.
    """

    user_content = f"""
    Student Submission:
    1. **Academic Progress and Vacation Plan:** {mte_data.get("academic_progress")}
    2. **Co and Extra Curricular Progress-Plan:** {mte_data.get("co-curricular")}
    3. **Financial Requirements for the next 3 months:** {mte_data.get("financial_needs")}
    4. **Difficulties (Social, Family, etc.):** {mte_data.get("difficulties")}
    5. **Results of the exams:** {mte_data.get("exam_results")}
    6. **Reading Books / Watching Videos:** {mte_data.get("books_and_videos")}
    7. **Exercise, Diet & Sleep:** {mte_data.get("health")}
    8. **Learning From Friends & Acquaintances:** {mte_data.get("learning_from_people")}
    9. **Essay on a topic of your choice:** {mte_data.get("essay")}
    10. **Action Plan for the coming month:** {mte_data.get("action_plan")}
    """

    return [
        {"role": "system", "content": system_content.strip()},
        {"role": "user", "content": user_content.strip()}
    ]

def extract_json(text):
    """
    Extracts a JSON block from the model's response, even if surrounded by extra formatting.
    """
    text = text.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    return text

def format_mte_data(mte_data):
    """
    Formats MTE data nicely into a text block (if needed for manual review/debugging).
    """
    formatted = ""
    for section, content in mte_data.items():
        section_title = section.replace("_", " ").title()
        formatted += f"### {section_title}:\n{content}\n\n"
    return formatted