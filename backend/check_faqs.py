# from app.database import SessionLocal
# from app.models import FAQ

# db = SessionLocal()

# faqs = db.query(FAQ).all()

# print(f"Total FAQs: {len(faqs)}")

# for faq in faqs:
#     print(faq.department, faq.category, faq.question)

from app.database import SessionLocal
from app.models import FAQ

db = SessionLocal()

faq = db.query(FAQ).first()

print(vars(faq))