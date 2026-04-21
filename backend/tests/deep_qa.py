import json
import sqlite3
import time
import uuid

import httpx

BASE = "http://127.0.0.1:8000"
JD = "Senior engineer role requiring Python APIs cloud architecture leadership." * 2


def run():
    results = {"multi_answer_session": {}, "invalid_input_cases": {}, "expiry_behavior": {}, "redis_cache_hint": {}}
    with httpx.Client(timeout=60.0) as client:
        sid = f"qa_{uuid.uuid4().hex[:8]}"
        setup = client.post(f"{BASE}/setup", json={"session_id": sid, "jd_text": JD, "interview_type": "technical"})
        results["multi_answer_session"]["setup_status"] = setup.status_code
        total_q = setup.json().get("total_questions", 0) if setup.status_code == 200 else 0
        for idx in range(total_q):
            ev = client.post(
                f"{BASE}/evaluate",
                json={
                    "session_id": sid,
                    "question_index": idx,
                    "answer": f"Answer {idx}: I delivered quantifiable impact with measurable outcomes and strong collaboration.",
                },
            )
            results["multi_answer_session"][f"eval_{idx}_status"] = ev.status_code
            results["multi_answer_session"][f"eval_{idx}_score"] = ev.json().get("overall") if ev.status_code == 200 else None
        rep = client.post(f"{BASE}/report", json={"session_id": sid})
        rep_json = rep.json() if rep.status_code == 200 else {}
        results["multi_answer_session"]["report_status"] = rep.status_code
        results["multi_answer_session"]["questions_answered"] = rep_json.get("detailed_metrics", {}).get("total_questions_answered")
        results["multi_answer_session"]["has_metrics"] = "detailed_metrics" in rep_json

        bad_setup = client.post(f"{BASE}/setup", json={"jd_text": "tiny", "interview_type": "technical"})
        bad_eval = client.post(f"{BASE}/evaluate", json={"session_id": sid, "question_index": 99, "answer": "valid answer text long enough"})
        missing_session = client.post(f"{BASE}/report", json={"session_id": "missing_123"})
        results["invalid_input_cases"] = {
            "short_jd_status": bad_setup.status_code,
            "invalid_question_index_status": bad_eval.status_code,
            "missing_session_report_status": missing_session.status_code,
        }

        sid2 = f"qaexp_{uuid.uuid4().hex[:8]}"
        setup2 = client.post(f"{BASE}/setup", json={"session_id": sid2, "jd_text": JD, "interview_type": "hr"})
        results["expiry_behavior"]["setup_status"] = setup2.status_code
        conn = sqlite3.connect("c:/Users/Administrator/Desktop/New folder/quantis_interview_grid.db")
        conn.execute("UPDATE interview_sessions SET expires_at = ? WHERE session_id = ?", ("2000-01-01 00:00:00+00:00", sid2))
        conn.commit()
        conn.close()
        time.sleep(0.2)
        after_exp = client.post(
            f"{BASE}/evaluate",
            json={"session_id": sid2, "question_index": 0, "answer": "I can still answer after expiration but should fail."},
        )
        results["expiry_behavior"]["evaluate_after_forced_expiry_status"] = after_exp.status_code

        try:
            import redis

            r = redis.Redis.from_url("redis://localhost:6379/0", decode_responses=True)
            key = f"session:{sid}"
            results["redis_cache_hint"]["redis_up"] = bool(r.ping())
            results["redis_cache_hint"]["cache_key_exists"] = bool(r.exists(key))
        except Exception:
            results["redis_cache_hint"]["redis_up"] = False
            results["redis_cache_hint"]["cache_key_exists"] = False

    print(json.dumps(results))


if __name__ == "__main__":
    run()

