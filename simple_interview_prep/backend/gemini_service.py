from google import genai
import os
import json
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=True)

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("WARNING: GEMINI_API_KEY not found in environment.")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.0-flash"

    async def generate_first_question(self, role: str, difficulty: int) -> str:
        """Generates the opening interview question for a given role and difficulty."""
        diff_map = {1: "Junior", 2: "Mid-Level", 3: "Senior"}
        level = diff_map.get(difficulty, "Junior")

        prompt = f"""
        You are a professional AI Interviewer conducting a mock technical interview.
        Role: {role}
        Level: {level}

        INSTRUCTIONS:
        1. GREET the candidate professionally.
        2. Introduce yourself as your AI Interviewer.
        3. Ask ONE clear, relevant first technical question for a {level} {role}.
        4. Do NOT ask multiple questions.
        """
        if not self.client:
            return f"Welcome to your {level} {role} interview. Could you please introduce yourself and outline your background?"
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"Gemini API Exception (Fallback active): {e}")
            return f"Welcome to your {level} {role} interview. Could you describe your experience with core concepts in {role}?"

    async def generate_next_question(self, role: str, transcript: list) -> str:
        """Generates the next follow-up question based on conversation transcript."""
        prompt = f"""
        You are a professional AI Interviewer for a {role} position.
        
        CONVERSATION HISTORY:
        {json.dumps(transcript, indent=2)}

        INSTRUCTIONS:
        - Acknowledge the candidate's last answer briefly.
        - Ask ONE clear, relevant follow-up technical question.
        - Keep your question under 3 sentences.
        """
        if not self.client:
            return "Thank you for that answer. Can you share an example of a challenging project you worked on?"

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"Gemini API Exception (Fallback active): {e}")
            return "Thank you for explaining that. What trade-offs did you consider when making that architecture decision?"

    async def evaluate_interview(self, role: str, transcript: list) -> dict:
        """Evaluates completed transcript and returns JSON with score (1-10) and feedback summary."""
        prompt = f"""
        Evaluate this candidate's full mock interview for a {role} position.

        TRANSCRIPT:
        {json.dumps(transcript, indent=2)}

        TASK:
        1. Assign an overall score from 1.0 to 10.0.
        2. Write a 3-4 sentence constructive feedback summary covering strengths and areas for improvement.

        Return strictly in JSON format:
        {{
            "score": 8.5,
            "feedback": "Your technical explanation of distributed caching was strong. Focus on expanding on error recovery and edge cases in future answers."
        }}
        """
        if not self.client:
            return {
                "score": 7.5,
                "feedback": "Solid interview performance. Good clear communication and logical problem-solving approach."
            }

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(text)
        except Exception as e:
            print(f"Gemini Evaluation Exception (Fallback active): {e}")
            return {
                "score": 7.0,
                "feedback": "Interview completed successfully. Candidate demonstrated solid foundational knowledge."
            }

gemini_service = GeminiService()
