from llm_chain import generate_quiz

NOTES = """
CSS Box Model: every HTML element is treated as a box made of four layers, from inside to outside: content, padding, border and margin. Padding is the space between the content and the border; margin is the space outside the border.
Servlets: a servlet is a Java class that handles HTTP requests on a server. The life cycle has three main methods: init() is called once when the servlet is loaded, service() handles each request (calling doGet() or doPost()), and destroy() is called when the servlet is removed.
Session tracking: HTTP is stateless, so a server uses cookies or the HttpSession object to recognise the same user across multiple requests.
Node.js: a JavaScript runtime that runs outside the browser; NPM is its package manager, and Express is a framework used to build RESTful APIs.
"""

quiz = generate_quiz(NOTES, num_questions=4)

for i, q in enumerate(quiz.questions, start=1):
    print(f"\nQ{i}. {q.question}")
    for j, opt in enumerate(q.options):
        print(f"   {'ABCD'[j]}. {opt}")
    print(f"   Answer: {'ABCD'[q.correct_index]}  |  {q.explanation}")