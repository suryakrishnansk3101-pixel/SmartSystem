from app.auth import verify_password

hashed = "$2b$12$test"

print("START")

print(
    verify_password(
        "admin123",
        hashed
    )
)

print("END")