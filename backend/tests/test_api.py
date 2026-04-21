from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def _auth_headers():
    import uuid

    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123!"
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 200
    l = client.post("/auth/login", json={"email": email, "password": password})
    assert l.status_code == 200
    token = l.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_setup_evaluate_report_flow():
    headers = _auth_headers()
    setup = client.post(
        "/setup",
        json={
            "jd_text": "Senior backend engineer role requiring Python, APIs, and architecture leadership." * 2,
            "interview_type": "technical",
        },
        headers=headers,
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
        headers=headers,
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
            headers=headers,
        )
        assert ev.status_code == 200

    report = client.post("/report", json={"session_id": sid, "transcript": [{"t": 1, "text": "hello"}]}, headers=headers)
    assert report.status_code == 200
    report_payload = report.json()
    assert "final_score" in report_payload
    assert "overall_assessment" in report_payload
    assert "hiring_likelihood" in report_payload
    assert isinstance(report_payload.get("next_steps"), list)
    assert "detailed_metrics" in report_payload
    assert isinstance(report_payload.get("preparation_resources"), list)

