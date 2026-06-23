import csv
import json

# Define components to programmatically build 360 distinct enterprise entries
departments = {
    "IT": {
        "topics": ["GitHub access", "VPN disconnection", "SSPR password reset", "Phishing email reporting", "Wi-Fi authentication", "Software license renewal", "Docker setup", "BitLocker recovery", "MFA device change", "Database backup access"],
        "actions": ["request", "troubleshoot", "verify standard policy for", "report an issue with", "get admin approval for"]
    },
    "HR": {
        "topics": ["Maternity/Paternity leave", "Form 16 tax download", "Hybrid work policy", "Emergency contact update", "Annual appraisal timeline", "Health insurance enrollment", "Reimbursement claims", "Notice period policy", "Onboarding checklist", "Provident fund withdrawal"],
        "actions": ["ask about", "submit a form for", "check the rules on", "update details for", "find timelines for"]
    },
    "Facilities": {
        "topics": ["Conference room booking", "AC/HVAC cooling leak", "Lost ID badge replacement", "Fire evacuation assembly", "Ergonomic chair request", "Office parking permit", "Catering for client events", "Janitorial service request", "Visitor access pre-clearance", "Desk relocation logistics"],
        "actions": ["book", "report a problem with", "request a replacement for", "verify safety rules for", "log a ticket for"]
    }
}

templates = [
    {"q": "How do I {} {}?", "a": "To {} {}, please log into the employee dashboard, navigate to the {} section, and follow the step-by-step wizard. If you experience errors, reply with the exact error code."},
    {"q": "What is the official procedure to {} {}?", "a": "The standard operating procedure for {} {} requires a formal submission via the portal. Processing typically takes 24-48 business hours pending departmental approval."},
    {"q": "I am having trouble trying to {} {}. Can you guide me?", "a": "No problem. To resolve issues with {} {}, ensure you are on the corporate network or connected via secure tunnel, then refresh your session. Let me know if you need me to open a ticket."},
    {"q": "Who do I contact if I need to {} {} immediately?", "a": "For urgent matters regarding {} {}, you can reach the dedicated {} helpdesk at extension 4400 or flag it as 'High Priority' in the system."},
]

dataset = []
id_counter = 1

# Generate 360 unique rows (3 departments * 10 topics * 3 actions * 4 templates)
for dept, data in departments.items():
    for topic in data["topics"]:
        # Mix actions to create structural variation
        for action in data["actions"][:3]: 
            for t in templates:
                q_text = t["q"].format(action, topic)
                # Simple programmatic smart answers
                a_text = t["a"].format(action, topic, dept)
                
                dataset.append({
                    "id": f"REQ-{id_counter:04d}",
                    "department": dept,
                    "category": topic.split()[0],
                    "question": q_text,
                    "answer": a_text
                })
                id_counter += 1

# Save as CSV
with open("enterprise_agent_qa.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "department", "category", "question", "answer"])
    writer.writeheader()
    writer.writerows(dataset)

# Save as JSON (Great for fine-tuning or feeding vector databases)
with open("enterprise_agent_qa.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=4)

print(f"Success! Generated {len(dataset)} unique Q&As in CSV and JSON formats.")