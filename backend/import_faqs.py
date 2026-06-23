import csv

from app.database import SessionLocal
from app.models import FAQ

db = SessionLocal()

count = 0

with open(
    "enterprise_agent_qa.csv",
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        existing = db.query(FAQ).filter(
            FAQ.question == row["question"]
        ).first()

        if not existing:

            faq = FAQ(
                department=row["department"],
                category=row["category"],
                question=row["question"],
                answer=row["answer"]
            )

            db.add(faq)
            count += 1

db.commit()

print(f"{count} new FAQs imported successfully!")