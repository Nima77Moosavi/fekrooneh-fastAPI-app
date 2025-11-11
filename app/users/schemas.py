from pydantic import BaseModel, ConfigDict, Field
from datetime import date


class UserCreate(BaseModel):
    username: str
    password: str
    xp: int


class UserRead(BaseModel):
    id: int
    username: str
    xp: int
    streak: int
    max_streak: int
    frozen_days: int
    last_checkin: date | None
    last_streak_reset: date | None

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None
    xp: int | None = None
    streak: int | None = None
    frozen_days: int | None = None


class UserLookup(BaseModel):
    username: str


class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str
