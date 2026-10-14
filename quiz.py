import random

from validator import MCQ, Quiz


def shuffle_options(q: MCQ, rng=random) -> MCQ:
    """Return a copy of the question with options in random order and correct_index updated."""
    correct_text = q.options[q.correct_index]
    options = q.options[:]
    rng.shuffle(options)
    return MCQ(
        question=q.question,
        options=options,
        correct_index=options.index(correct_text),
        explanation=q.explanation,
    )


def shuffle_quiz(quiz: Quiz, seed: int | None = None) -> Quiz:
    rng = random.Random(seed)
    return Quiz(questions=[shuffle_options(q, rng) for q in quiz.questions])


def score_quiz(quiz: Quiz, answers: dict[int, int]) -> dict:
    """answers maps question number (0-based) -> chosen option index."""
    correct = 0
    review = []
    for i, q in enumerate(quiz.questions):
        chosen = answers.get(i)
        is_correct = chosen == q.correct_index
        correct += is_correct
        review.append({
            "question": q.question,
            "your_answer": q.options[chosen] if chosen is not None else None,
            "correct_answer": q.options[q.correct_index],
            "is_correct": is_correct,
            "explanation": q.explanation,
        })
    total = len(quiz.questions)
    return {
        "score": correct,
        "total": total,
        "percent": round(100 * correct / total) if total else 0,
        "review": review,
    }


if __name__ == "__main__":
    q = MCQ(
        question="What does CSS stand for?",
        options=["Cascading Style Sheets", "Computer Style Sheets",
                 "Creative Style System", "Colorful Style Sheets"],
        correct_index=0,
        explanation="CSS stands for Cascading Style Sheets.",
    )
    shuffled = shuffle_quiz(Quiz(questions=[q]), seed=1)
    sq = shuffled.questions[0]

    print("Options:", sq.options)
    print("Correct:", sq.options[sq.correct_index])
    print("All right ->", score_quiz(shuffled, {0: sq.correct_index})["percent"], "%")
    print("All wrong ->", score_quiz(shuffled, {0: (sq.correct_index + 1) % 4})["percent"], "%")