from datetime import date, time

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import WorkingScheduleStatus

class WorkingScheduleCreate(BaseModel):
    doctor_id: int = Field(gt=0)

    work_date: date

    start_time: time

    end_time: time

    status: WorkingScheduleStatus = (WorkingScheduleStatus.ACTIVE)

    @model_validator(mode="after")
    def validate_time(self):

        if self.start_time >= self.end_time:
            raise ValueError("Start time phai nho hon end time")

        return self

class WorkingScheduleUpdate(BaseModel):
    work_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None

    status: WorkingScheduleStatus | None = None

    @model_validator(mode="after")
    def validate_time(self):
        if(
            self.start_time is not None
            and self.end_time is not None
            and self.start_time >= self.end_time
        ):
            raise ValueError("Start time phai nho hon end time")

        return self

class WorkingScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    schedule_id: int

    doctor_id: int

    work_date: date

    start_time: time

    end_time: time

    status: WorkingScheduleStatus


