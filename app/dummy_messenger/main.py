from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session
from dummy_messenger import models
import database

app = FastAPI(title="Dummy Messenger")


class MessageRequest(BaseModel):
    user_name: str = Field(
        ..., max_length=64, min_length=3,
        description="Имя пользователя должно быть от 3 до 64 символов."
        )
    message: str = Field(
        ..., max_length=1024, min_length=10,
        description="Сообщение должно быть от 10 до 1024 символов."
        )

    @field_validator('user_name')
    def validate_user_name(cls, value):
        if not value.isalnum():
            raise ValueError("Имя пользователя должно содержать только буквы и цифры.")  # noqa
        return value

    @field_validator('message')
    def validate_message(cls, value):
        if value.strip() == "":
            raise ValueError("Сообщение не может быть пустым.")
        return value

    class Config:
        min_anystr_length = 1
        anystr_strip_whitespace = True


@app.post("/send_message/")
async def send_message(message: MessageRequest, db: Session = Depends(database.get_db_url)):  # noqa
    try:
        db_message = models.UserMessages(
            user_name=message.user_name,
            message=message.message
        )
        db.add(db_message)
        db.commit()

        messages = db.query(models.UserMessages).order_by(models.UserMessages.created_at.desc()).limit(10).all()  # noqa

        return [
            {
                "sender_name": msg.user_name,
                "text": msg.message,
                "timestamp": msg.created_at,
                "message_number": msg.id,
                "message_count": sum(
                    1 for m in messages if m.user_name == msg.user_name
                )
            }
            for msg in messages
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
