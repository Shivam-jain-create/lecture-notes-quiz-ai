from pydantic import BaseModel, Field, field_validator, model_validator


class MCQ(BaseModel):
    question: str = Field(description="A clear question based only on the provided notes")
    options: list[str] = Field(description="Exactly 4 distinct answer options")
    correct_index: int = Field(description="Index (0 to 3) of the correct option in 'options'")
    explanation: str = Field(description="One sentence explaining why the answer is correct")

    @field_validator("question", "explanation")
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be empty")
        return v

    @model_validator(mode="after")
    def check_options(self):
        opts = [o.strip() for o in self.options]
        if len(opts) != 4:
            raise ValueError("need exactly 4 options")
        if any(not o for o in opts):
            raise ValueError("options must not be empty")
        if len({o.lower() for o in opts}) != 4:
            raise ValueError("options must be distinct")
        if not 0 <= self.correct_index <= 3:
            raise ValueError("correct_index must be between 0 and 3")
        self.options = opts
        return self


class Quiz(BaseModel):
    questions: list[MCQ]


if __name__ == "__main__":
    good = {
        "question": "What does CSS stand for?",
        "options": ["Cascading Style Sheets", "Computer Style Sheets",
                    "Creative Style System", "Colorful Style Sheets"],
        "correct_index": 0,
        "explanation": "CSS stands for Cascading Style Sheets.",
    }
    print("GOOD ->", MCQ(**good).question)

    bad_cases = {
        "only 3 options": {**good, "options": good["options"][:3]},
        "correct_index out of range": {**good, "correct_index": 5},
        "duplicate options": {**good, "options": ["A", "a", "B", "C"]},
    }
    for name, data in bad_cases.items():
        try:
            MCQ(**data)
            print(f"BAD ({name}) -> NOT caught!")
        except ValueError:
            print(f"BAD ({name}) -> rejected")