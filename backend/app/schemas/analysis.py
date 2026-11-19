from pydantic import BaseModel, ConfigDict,  Field


class TaskAnalysis(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        strict= True,
    )

    goal:str = Field(min_length=1, max_length=1000)
    expected_deliverable:str = Field(min_length=1, max_length=1000)
    missing_information: list[str]