from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from backend.app.config import settings
from backend.app.repositories.session_repository import SessionRepository
from backend.app.schemas import Session
from backend.app.services.ai_client import GroqClient
from backend.app.services.cache import SessionCache

DIMENSIONS = ["relevance", "clarity", "depth", "structure", "confidence"]
WEIGHTS = {"relevance": 0.25, "clarity": 0.20, "depth": 0.25, "structure": 0.20, "confidence": 0.10}


class InterviewService:
    def __init__(self, ai_client: GroqClient, session_repository: SessionRepository, session_cache: SessionCache) -> None:
        self.ai_client = ai_client
        self.session_repository = session_repository
        self.session_cache = session_cache

    def clean_expired(self) -> None:
        self.session_repository.cleanup_expired()

    def setup(self, jd_text: str, interview_type: str, session_id: str | None = None) -> dict[str, Any]:
        self.clean_expired()
        sid = session_id or f"session_{uuid4().hex[:12]}"
        analysis = self._analyze_jd(jd_text)
        questions = self._generate_questions(analysis, interview_type)
        now = datetime.now(timezone.utc)
        session = Session(
            created_at=now,
            expires_at=now + timedelta(minutes=settings.session_ttl_minutes),
            jd_analysis=analysis,
            interview_type=interview_type,
            questions=questions,
        )
        self.session_repository.save(sid, session, raw_jd=jd_text[:8000])
        self.session_cache.set(sid, session.model_dump_json(), settings.session_ttl_minutes * 60)
        return {"session_id": sid, "jd_analysis": analysis, "questions": questions, "total_questions": len(questions)}

    def evaluate(self, session_id: str, question_index: int, answer: str) -> dict[str, Any] | None:
        self.clean_expired()
        session = self._get_session(session_id)
        if not session or question_index >= len(session.questions):
            return None
        # Save answer only; full scoring happens in final report.
        normalized_answer = answer.strip()
        if question_index < len(session.answers):
            session.answers[question_index] = normalized_answer
        else:
            while len(session.answers) < question_index:
                session.answers.append("")
            session.answers.append(normalized_answer)
        session.evaluations = []
        self.session_repository.save(session_id, session)
        self.session_cache.set(session_id, session.model_dump_json(), settings.session_ttl_minutes * 60)
        answered = len([a for a in session.answers if a.strip()])
        return {
            "accepted": True,
            "question_index": question_index,
            "answered_count": answered,
            "remaining_count": max(0, len(session.questions) - answered),
            "message": "Answer recorded. Final scoring will be generated after all questions.",
        }

    def report(self, session_id: str) -> dict[str, Any] | None:
        self.clean_expired()
        session = self._get_session(session_id)
        if not session:
            return None
        answered_questions = [a for a in session.answers if a.strip()]
        if len(answered_questions) < len(session.questions):
            return {"incomplete": True, "answered": len(answered_questions), "total": len(session.questions)}

        if len(session.evaluations) != len(session.questions):
            session.evaluations = [
                self._evaluate_answer(q, a, session.jd_analysis.get("role_title", "Role"), session.interview_type)
                for q, a in zip(session.questions, session.answers)
            ]
            self.session_repository.save(session_id, session)
            self.session_cache.set(session_id, session.model_dump_json(), settings.session_ttl_minutes * 60)

        avg_scores = {d: round(sum(ev["scores"].get(d, 0) for ev in session.evaluations) / len(session.evaluations)) for d in DIMENSIONS}
        question_totals = [ev["overall"] for ev in session.evaluations]
        final_score = round(sum(question_totals) / len(question_totals))
        trend = "improving" if len(question_totals) > 1 and question_totals[-1] > question_totals[0] else "steady"
        consistency = round(100 - (max(question_totals) - min(question_totals))) if question_totals else 0
        narrative = self._generate_report_narrative(session, avg_scores, final_score)
        return {
            "final_score": final_score,
            "avg_scores": avg_scores,
            "grade": "A" if final_score >= 85 else "B" if final_score >= 70 else "C" if final_score >= 55 else "D" if final_score >= 40 else "F",
            "question_scores": [{"question": q, "score": ev["overall"]} for q, ev in zip(session.questions, session.evaluations)],
            "overall_assessment": narrative["overall_assessment"],
            "hiring_likelihood": narrative["hiring_likelihood"],
            "next_steps": narrative["next_steps"],
            "detailed_metrics": {
                "total_questions_answered": len(question_totals),
                "score_trend": trend,
                "consistency_index": max(0, min(100, consistency)),
                "best_dimension": max(avg_scores, key=avg_scores.get) if avg_scores else "",
                "weakest_dimension": min(avg_scores, key=avg_scores.get) if avg_scores else "",
                "pace": "dynamic",
                "completion_rate": round((len(answered_questions) / len(session.questions)) * 100),
                "average_answer_words": round(
                    sum(len(a.split()) for a in session.answers if a.strip()) / max(1, len(answered_questions)), 1
                ),
            },
            "preparation_resources": self._resource_suggestions(session.interview_type, min(avg_scores, key=avg_scores.get)),
        }

    def has_session(self, session_id: str) -> bool:
        self.clean_expired()
        return self.session_repository.exists(session_id)

    def _get_session(self, session_id: str) -> Session | None:
        cached = self.session_cache.get(session_id)
        if cached:
            try:
                return Session.model_validate_json(cached)
            except Exception:
                self.session_cache.delete(session_id)
        session = self.session_repository.get(session_id)
        if session:
            self.session_cache.set(session_id, session.model_dump_json(), settings.session_ttl_minutes * 60)
        return session

    def _analyze_jd(self, jd_text: str) -> dict[str, Any]:
        fallback = {
            "role_title": "Software Engineer",
            "company_type": "unknown",
            "seniority": "mid",
            "top_skills": [],
            "key_responsibilities": [],
            "interview_focus": "Core role fit, problem-solving, and communication.",
            "difficulty": "medium",
        }
        prompt = f"""
Return valid JSON only with keys:
role_title, company_type, seniority, top_skills, key_responsibilities, interview_focus, difficulty.
Use difficulty one of: easy, medium, hard.
Use top_skills length <= 6 and key_responsibilities length <= 5.

JOB DESCRIPTION:
{jd_text[:4000]}
"""
        data = self.ai_client.chat_json(prompt, fallback)
        merged = {**fallback, **(data or {})}
        merged["difficulty"] = merged["difficulty"] if merged["difficulty"] in {"easy", "medium", "hard"} else "medium"
        return merged

    def _generate_questions(self, analysis: dict[str, Any], interview_type: str) -> list[str]:
        fallback = self._template_questions(analysis, interview_type)
        count = {"easy": 5, "medium": 7, "hard": 8}.get(analysis.get("difficulty", "medium"), 7)
        prompt = f"""
Return valid JSON only with key 'questions' as an array of exactly {count} strings.
Interview type: {interview_type}
Role: {analysis.get("role_title")}
Skills: {analysis.get("top_skills", [])}
Responsibilities: {analysis.get("key_responsibilities", [])}
Focus: {analysis.get("interview_focus", "")}
Generate realistic recruiter/interviewer questions tied to THIS exact role context.
Avoid generic filler. Every question must reference either skills, responsibilities, or seniority expectations.
"""
        data = self.ai_client.chat_json(prompt, {"questions": fallback})
        questions = data.get("questions", [])
        if not isinstance(questions, list):
            return fallback[:count]
        cleaned = [q.strip() for q in questions if isinstance(q, str) and len(q.strip()) > 10]
        if len(cleaned) < max(3, count // 2):
            return fallback[:count]
        return cleaned[:count]

    def _evaluate_answer(self, question: str, answer: str, role: str, interview_type: str) -> dict[str, Any]:
        if not self.ai_client.available():
            scores = {d: 60 for d in DIMENSIONS}
            overall = round(sum(scores[d] * WEIGHTS[d] for d in DIMENSIONS))
            return {
                "scores": scores,
                "overall": overall,
                "feedback": "Groq API key missing. Running in fallback scoring mode.",
                "strengths": ["Answer was submitted and processed."],
                "improvements": ["Set GROQ_API_KEY to enable full AI feedback."],
                "model_answer_hint": "",
            }

        fallback = {
            "scores": {"relevance": 55, "clarity": 55, "depth": 55, "structure": 55, "confidence": 55},
            "feedback": "Your answer is directionally strong. Add one concrete metric and tighten the structure using STAR.",
            "strengths": ["You addressed the question directly."],
            "improvements": ["Include measurable impact.", "Use clearer step-by-step flow."],
            "model_answer_hint": "A strong response includes context, action specifics, and quantified outcomes.",
        }
        prompt = f"""
Return valid JSON only with this shape:
{{
  "scores": {{
    "relevance": 0-100,
    "clarity": 0-100,
    "depth": 0-100,
    "structure": 0-100,
    "confidence": 0-100
  }},
  "feedback": "2 concise actionable sentences",
  "strengths": ["...", "..."],
  "improvements": ["...", "..."],
  "model_answer_hint": "one sentence"
}}

Role: {role}
Interview type: {interview_type}
Question: {question}
Answer: {answer}
"""
        parsed = self.ai_client.chat_json(prompt, fallback)
        raw_scores = parsed.get("scores", {})
        scores = {d: max(0, min(100, int(raw_scores.get(d, 50)))) for d in DIMENSIONS}
        overall = round(sum(scores[d] * WEIGHTS[d] for d in DIMENSIONS))
        return {
            "scores": scores,
            "overall": overall,
            "feedback": str(parsed.get("feedback", fallback["feedback"])),
            "strengths": [s for s in parsed.get("strengths", []) if isinstance(s, str)][:3],
            "improvements": [i for i in parsed.get("improvements", []) if isinstance(i, str)][:3],
            "model_answer_hint": str(parsed.get("model_answer_hint", fallback["model_answer_hint"])),
        }

    def _generate_report_narrative(self, session: Session, avg_scores: dict[str, int], final_score: int) -> dict[str, Any]:
        fallback = {
            "overall_assessment": "You show a solid baseline and can improve by giving more specific evidence and clearer structure.",
            "hiring_likelihood": "Borderline - promising profile with room to improve consistency.",
            "next_steps": [
                "Practice 5 STAR stories with quantified outcomes.",
                "Reduce filler words and tighten opening statements.",
                "Rehearse role-specific technical depth on top 3 skills.",
            ],
        }
        if not self.ai_client.available():
            return fallback
        prompt = f"""
Return valid JSON only:
{{
  "overall_assessment": "3 concise sentences",
  "hiring_likelihood": "Strong Yes/Lean Yes/Borderline/Lean No/Strong No - one sentence reason",
  "next_steps": ["step 1", "step 2", "step 3"]
}}

Role: {session.jd_analysis.get("role_title", "Unknown")}
Interview type: {session.interview_type}
Final score: {final_score}
Average scores: {avg_scores}
Question scores: {[ev.get("overall", 0) for ev in session.evaluations]}
"""
        parsed = self.ai_client.chat_json(prompt, fallback)
        next_steps = [s for s in parsed.get("next_steps", []) if isinstance(s, str)][:3]
        if not next_steps:
            next_steps = fallback["next_steps"]
        return {
            "overall_assessment": str(parsed.get("overall_assessment", fallback["overall_assessment"])),
            "hiring_likelihood": str(parsed.get("hiring_likelihood", fallback["hiring_likelihood"])),
            "next_steps": next_steps,
        }

    @staticmethod
    def _resource_suggestions(interview_type: str, weakest_dimension: str) -> list[dict[str, str]]:
        base = [
            {"title": "STAR Method Guide", "url": "https://www.themuse.com/advice/star-interview-method", "why": "Improve structure and storytelling."},
            {"title": "LeetCode Interview Practice", "url": "https://leetcode.com/", "why": "Practice technical problem-solving."},
            {"title": "System Design Primer", "url": "https://github.com/donnemartin/system-design-primer", "why": "Strengthen architecture depth."},
            {"title": "PM Interview Prep", "url": "https://www.productalliance.com/", "why": "Sharpen product thinking and metrics."},
            {"title": "Behavioral Questions Bank", "url": "https://www.indeed.com/career-advice/interviewing/top-interview-questions-and-answers", "why": "Prepare high-frequency interview questions."},
        ]
        if interview_type == "technical":
            return [base[1], base[2], base[0]]
        if interview_type == "product":
            return [base[3], base[0], base[4]]
        if weakest_dimension == "structure":
            return [base[0], base[4], base[2]]
        return [base[4], base[0], base[1]]

    @staticmethod
    def _template_questions(analysis: dict[str, Any], interview_type: str) -> list[str]:
        role = analysis.get("role_title", "this role")
        skills = analysis.get("top_skills", []) or ["core skill"]
        responsibilities = analysis.get("key_responsibilities", []) or ["deliver outcomes"]
        primary_skill = skills[0]
        primary_resp = responsibilities[0]
        bank = {
            "technical": [
                f"For the {role} role, walk me through how you would architect a solution for: {primary_resp}.",
                f"What are the key trade-offs when implementing {primary_skill} at production scale?",
                f"Describe a recent performance or reliability issue you solved and the debugging path you followed.",
                "How would you design observability for this system from day one?",
                "Explain how you prioritize technical debt against feature delivery.",
                "How would you handle a breaking production incident in your first month?",
                "What system design interview question would you ask a peer for this role, and how would you answer it?",
            ],
            "behavioral": [
                f"Tell me about a time you delivered {primary_resp} under pressure.",
                f"Describe a conflict with a stakeholder while working on {primary_skill} and how you resolved it.",
                "Give an example of when your first approach failed and how you adapted.",
                "Tell me about a time you mentored someone and what changed as a result.",
                "Describe a decision you made with incomplete information and its outcome.",
                "Share a project where communication quality changed the result.",
                "What feedback do you receive most often, and what have you done with it?",
            ],
            "product": [
                f"How would you define success metrics for a product initiative focused on {primary_resp}?",
                f"How would you prioritize roadmap items involving {primary_skill} with limited engineering bandwidth?",
                "Describe how you would validate user demand before shipping.",
                "What trade-offs would you make between growth and reliability in this domain?",
                "How do you present product decisions to technical and non-technical stakeholders?",
                "Walk through a product decision you changed after looking at metrics.",
                "How would you run an experiment to improve activation in the first 7 days?",
            ],
            "leadership": [
                f"How would you organize a team to consistently deliver on {primary_resp}?",
                "Describe a situation where team performance dropped and how you recovered it.",
                "How do you make hiring decisions for senior talent?",
                "How do you balance strategic work versus urgent execution for your team?",
                "Tell me about a difficult cross-team alignment you led.",
                "How do you coach underperforming team members while maintaining standards?",
                "How do you communicate vision to executives and ICs differently?",
            ],
            "hr": [
                f"Why are you interested in this {role} position specifically?",
                "What are your strongest strengths and where are you actively improving?",
                "How do you handle fast-changing priorities in a new role?",
                "What kind of manager and team environment helps you do your best work?",
                "What motivates you to stay long-term at a company?",
                "Tell me about your compensation expectations and decision criteria.",
                "What questions do you have for us about role expectations and growth?",
            ],
        }
        return bank.get(interview_type, bank["behavioral"])

