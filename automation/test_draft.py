# automation/test_draft.py

from automation.gmail_draft import create_draft

result = create_draft(
    to_email="pk3255207@gmail.com",
    subject="TEST DRAFT – RAG SYSTEM",
    body="This is a test draft created via Gmail API."
)

print(result)
