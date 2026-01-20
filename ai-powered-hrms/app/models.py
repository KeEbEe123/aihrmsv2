from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from typing import List, Optional


@dataclass
class Teacher:
    id: int
    name: str
    phone: str
    department: Optional[str] = None
    subjects: Optional[List[str]] = None
    workload: Optional[int] = None


@dataclass
class Admin:
    id: int
    name: str
    phone: str


@dataclass
class Timetable:
    teacher_id: int
    day_of_week: int  # 0=Mon
    start_time: time
    end_time: time
    clazz: str
    subject: str


@dataclass
class Leave:
    id: Optional[int]
    teacher_id: int
    start_date: date
    end_date: date
    reason: Optional[str]
    status: str  # pending/approved/rejected


@dataclass
class Substitution:
    id: Optional[int]
    leave_id: int
    substitute_teacher_id: int
    status: str  # pending/confirmed/rejected


@dataclass
class Notification:
    id: Optional[int]
    target_phone: str
    message: str
    twilio_sid: Optional[str]
    status: str  # queued/sent/failed


