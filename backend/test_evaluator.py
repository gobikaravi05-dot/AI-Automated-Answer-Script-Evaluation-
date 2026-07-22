from ai.evaluator import evaluate_answer

question = "What is Artificial Intelligence?"

answer_key = """
Artificial Intelligence is the simulation of human intelligence by machines.
It includes learning, reasoning, problem solving and decision making.
"""

student_answer = """
Artificial Intelligence is making computers think like humans.
It helps machines learn and solve problems.
"""

result = evaluate_answer(
    question,
    answer_key,
    student_answer
)

print("===== EVALUATION =====")
print(result)