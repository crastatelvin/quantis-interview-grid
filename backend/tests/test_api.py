from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_setup_evaluate_report_flow():
    setup = client.post(
        "/setup",
        json={
            "jd_text": "Senior backend engineer role requiring Python, APIs, and architecture leadership." * 2,
            "interview_type": "technical",
        },
    )
    assert setup.status_code == 200
    payload = setup.json()
    sid = payload["session_id"]
    assert payload["total_questions"] >= 5

    evaluate = client.post(
        "/evaluate",
        json={
            "session_id": sid,
            "question_index": 0,
            "answer": "I led an API platform redesign, reduced latency by 40 percent, and improved reliability with proper observability.",
        },
    )
    assert evaluate.status_code == 200
    assert evaluate.json().get("accepted") is True

    for idx in range(1, payload["total_questions"]):
        ev = client.post(
            "/evaluate",
            json={
                "session_id": sid,
                "question_index": idx,
                "answer": f"I handled scenario {idx} with measurable impact and clear communication.",
            },
        )
        assert ev.status_code == 200

    report = client.post("/report", json={"session_id": sid})
    assert report.status_code == 200
    report_payload = report.json()
    assert "final_score" in report_payload
    assert "overall_assessment" in report_payload
    assert "hiring_likelihood" in report_payload
    assert isinstance(report_payload.get("next_steps"), list)
    assert "detailed_metrics" in report_payload
    assert isinstance(report_payload.get("preparation_resources"), list)

