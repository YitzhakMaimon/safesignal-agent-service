import io
import os
import uuid
import json
import urllib.request
import boto3
import pandas as pd
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request, session as flask_session, jsonify, Response
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = os.environ.get("SECRET_KEY", "safesignal-secret-key")

AGENT_ID       = os.environ.get("AGENT_ID", "INDHHZGRD2")
AGENT_ALIAS_ID = os.environ.get("AGENT_ALIAS_ID", "E4SR5MTKOO")
bedrock_runtime = boto3.client(service_name="bedrock-agent-runtime", region_name="us-east-1")

GENERAL_KEYWORDS = ["בירת", "צרפת", "מתמטיקה", "תרגיל", "היסטוריה", "גאוגרפיה", "קוד פיתון", "תכנת לי"]


def parse_agent_response(completion):
    result_text   = ""
    sources       = []
    category      = None
    lambda_called = False
    history       = {}

    for event in completion:
        if "trace" in event:
            trace = event["trace"].get("trace", {})
            orch  = trace.get("orchestrationTrace", {})

            inv = orch.get("invocationInput", {})
            ag  = inv.get("actionGroupInvocationInput", {})
            if ag:
                func   = ag.get("function", "")
                params = {p["name"]: p["value"] for p in ag.get("parameters", [])}
                if func == "send_alert":
                    lambda_called = True
                    category = int(params.get("category", 2))
                elif "category" in params and category is None:
                    category = int(params.get("category", 2))

            obs     = orch.get("observation", {})
            ag_out  = obs.get("actionGroupInvocationOutput", {})
            ag_text = ag_out.get("text", "")
            if ag_text:
                try:
                    data = json.loads(ag_text)
                    if "total" in data:
                        history = data
                except Exception:
                    pass

        chunk = event.get("chunk", {})
        if "bytes" in chunk:
            result_text += chunk["bytes"].decode("utf-8")
        for citation in chunk.get("attribution", {}).get("citations", []):
            for ref in citation.get("retrievedReferences", []):
                s3_uri    = ref.get("location", {}).get("s3Location", {}).get("uri", "")
                file_name = s3_uri.split("/")[-1] if s3_uri else "מקור מערכת"
                text_chunk = ref.get("content", {}).get("text", "")
                entry = {"file": file_name, "text": text_chunk}
                if entry not in sources:
                    sources.append(entry)

    return result_text, sources, category, lambda_called, history


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_text = request.form.get("user_text", "").strip()
        user_id   = request.remote_addr or "anonymous"

        if not user_text:
            return render_template("index.html", error="אנא הזן טקסט לבדיקה.")

        if any(keyword in user_text for keyword in GENERAL_KEYWORDS):
            return render_template(
                "index.html",
                result="מצטער, המידע המבוקש אינו קיים במסמכי המערכת ואין לי אפשרות לענות על שאלות כלליות.",
                sources=[], original_text=user_text
            )

        try:
            session_id = str(uuid.uuid4())

            history_lines = flask_session.get("chat_history", [])
            history_context = ""
            if history_lines:
                history_context = "היסטוריית שיחה:\n" + "\n".join(history_lines[-6:]) + "\n\n"

            input_text = f"[user_id:{user_id}|session_id:{session_id}]\n{history_context}{user_text}"

            response = bedrock_runtime.invoke_agent(
                agentId=AGENT_ID,
                agentAliasId=AGENT_ALIAS_ID,
                sessionId=session_id,
                inputText=input_text,
                enableTrace=True
            )

            result_text, sources, category, lambda_called, history = parse_agent_response(
                response.get("completion", [])
            )

            if not result_text:
                result_text = "לא התקבלה תשובה מהסוכן."

            display_text = result_text.replace("[ALERT: TRUE]", "").replace("[ALERT:TRUE]", "").replace('\\"', '"').strip()

            chat_history = flask_session.get("chat_history", [])
            chat_history.append(f"שאלה: {user_text}")
            chat_history.append(f"תשובה: {display_text[:200]}")
            flask_session["chat_history"] = chat_history[-12:]
            flask_session.modified = True

            alert_sent = None
            if lambda_called and category:
                alert_sent = "נשלח מייל לגורמים הרלוונטיים"
                flask_session["email_sent"] = True
                flask_session.modified = True
                print(f"*** [SafeSignal] ALERT — category {category} — user: {user_id} ***")

            # Show count from PREVIOUS incidents only (subtract current one)
            prev_total = max(0, history.get("total", 0) - 1)

            return render_template("index.html",
                result=display_text, sources=sources,
                original_text=user_text, category=category,
                alert_sent=alert_sent,
                history_total=prev_total,
                history_first=history.get("first_seen", ""))

        except Exception as e:
            return render_template("index.html", error=f"שגיאה בתקשורת מול AWS Bedrock Agent: {str(e)}")

    return render_template("index.html")


@app.route("/status")
def status():
    ec2_ok = True

    agent_ok = False
    try:
        client = boto3.client("bedrock-agent", region_name="us-east-1")
        client.get_agent(agentId=AGENT_ID)
        agent_ok = True
    except Exception:
        pass

    return jsonify({
        "ec2":   ec2_ok,
        "agent": agent_ok,
        "email": flask_session.get("email_sent", False)
    })


@app.route("/export-csv")
def export_csv():
    try:
        table = dynamodb.Table("SafeSignalHistory")
        items = table.scan().get("Items", [])
    except Exception:
        items = []

    df = pd.DataFrame([{
        "timestamp":    i.get("timestamp", ""),
        "user_id":      i.get("user_id", ""),
        "category":     i.get("category", ""),
        "text_snippet": i.get("text_snippet", ""),
        "session_id":   i.get("session_id", ""),
    } for i in sorted(items, key=lambda x: x.get("timestamp", ""), reverse=True)])

    buf = io.StringIO()
    df.to_csv(buf, index=False, encoding="utf-8-sig")
    return Response(
        buf.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=safesignal_incidents.csv"}
    )


@app.route("/history")
def history():
    from datetime import datetime, timezone, timedelta
    IL = timezone(timedelta(hours=3))
    try:
        table = dynamodb.Table("SafeSignalHistory")
        resp  = table.scan()
        items = sorted(resp.get("Items", []), key=lambda x: x.get("timestamp", ""), reverse=True)
        for item in items:
            ts = item.get("timestamp", "")
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    item["timestamp"] = dt.astimezone(IL).strftime("%Y-%m-%dT%H:%M:%S")
                except Exception:
                    pass
    except Exception:
        items = []
    return render_template("history.html", items=items)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
