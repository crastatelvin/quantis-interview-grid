import json
import uuid

import httpx

base = "http://127.0.0.1:8000"
jd = "Senior engineer role requiring Python APIs cloud architecture leadership." * 2
types = ["technical", "behavioral", "product", "leadership", "hr"]
out = []
first_questions = {}

with httpx.Client(timeout=60.0) as client:
    for interview_type in types:
        sid = f"test_{uuid.uuid4().hex[:8]}"
        setup = client.post(
            f"{base}/setup",
            json={"jd_text": jd, "interview_type": interview_type, "session_id": sid},
        )
        setup_ok = setup.status_code == 200 and len(setup.json().get("questions", [])) > 0
        setup_questions = setup.json().get("questions", [])
        if setup_questions:
            first_questions[interview_type] = setup_questions[0]

        eval_ok = True
        for idx in range(len(setup_questions)):
            evaluate = client.post(
                f"{base}/evaluate",
                json={
                    "session_id": sid,
                    "question_index": idx,
                    "answer": f"Answer {idx}: I led a platform modernization, cut latency 38 percent, and improved reliability with observability.",
                },
            )
            eval_ok = eval_ok and evaluate.status_code == 200 and evaluate.json().get("accepted") is True

        report = client.post(f"{base}/report", json={"session_id": sid})
        report_data = report.json() if report.status_code == 200 else {}
        report_ok = (
            report.status_code == 200
            and "final_score" in report_data
            and "overall_assessment" in report_data
            and isinstance(report_data.get("next_steps"), list)
            and "detailed_metrics" in report_data
            and isinstance(report_data.get("preparation_resources"), list)
        )
        out.append(
            {
                "type": interview_type,
                "setup": setup_ok,
                "evaluate": eval_ok,
                "report": report_ok,
                "status_codes": [setup.status_code, report.status_code],
                "sample_score": report_data.get("final_score"),
            }
        )

print(json.dumps({"results": out, "first_questions": first_questions}))

