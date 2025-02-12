from flask import Flask, render_template, request, session, jsonify, url_for
from word_database import get_quiz

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.route("/")
def index():
    session["quiz"] = get_quiz()
    session["score"] = 0
    session["current_question"] = 0
    session["wrong_answers"] = []
    
    return render_template("index.html")

@app.route("/next", methods=["POST", "GET"])
def next_question():
    quiz = session["quiz"]
    current_question = session["current_question"]

    # 如果测试已完成，返回结果页面
    if current_question >= len(quiz):
        return jsonify({"finished": True, "redirect_url": url_for("result")})

    # 处理 POST 请求（用户提交答案）
    if request.method == "POST":
        user_answer = request.json.get("answer")  
        correct_answer = quiz[current_question]["correct_answer"]
        is_correct = (user_answer == correct_answer)

        if user_answer:
            if is_correct:
                session["score"] += 1
            else:
                session["wrong_answers"].append({
                    "english": quiz[current_question]["english"],
                    "correct": correct_answer,
                    "your_answer": user_answer
                })

        # 递增 `current_question`
        session["current_question"] += 1

        # 处理最后一题后直接跳转
        if session["current_question"] >= len(quiz):
            return jsonify({"finished": True, "redirect_url": url_for("result")})

        next_question = quiz[session["current_question"]]
        progress = int((session["current_question"] / len(quiz)) * 100)

        return jsonify({
            "finished": False,
            "question_number": session["current_question"] + 1,
            "english": next_question["english"],
            "options": next_question["options"],
            "correct": correct_answer,
            "is_correct": is_correct,
            "progress": progress
        })

    # 处理 GET 请求（初始化页面时）
    progress = int((session["current_question"] / len(quiz)) * 100)
    return jsonify({
        "finished": False,
        "question_number": current_question + 1,
        "english": quiz[current_question]["english"],
        "options": quiz[current_question]["options"],
        "correct": None,  # GET 请求不返回正确答案
        "progress": progress
    })

@app.route("/result")
def result():
    return render_template("result.html", 
                           score=session["score"], 
                           total=len(session["quiz"]), 
                           wrong_answers=session["wrong_answers"])

if __name__ == "__main__":
    app.run(debug=True)
