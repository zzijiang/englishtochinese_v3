from flask import Flask, render_template, request, redirect, url_for, session
from word_database import get_quiz

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.route("/")
def index():
    session["quiz"] = get_quiz()
    session["score"] = 0
    session["current_question"] = 0
    session["wrong_answers"] = []  # 新增：存储错题
    return render_template("index.html", question=session["quiz"][0], question_number=1)

@app.route("/next", methods=["POST"])
def next_question():
    user_answer = request.form.get("answer")
    current_question = session["current_question"]
    
    # 获取当前题目的正确答案
    correct_answer = session["quiz"][current_question]["correct_answer"]
    english_word = session["quiz"][current_question]["english"]

    # 检查用户答案
    if user_answer == correct_answer:
        session["score"] += 1
    else:
        # 记录错题（包含单词、正确答案、用户答案）
        session["wrong_answers"].append({
            "english": english_word,
            "correct": correct_answer,
            "your_answer": user_answer
        })

    session["current_question"] += 1

    # 如果题目完成，跳转到结果页
    if session["current_question"] >= len(session["quiz"]):
        return redirect(url_for("result"))

    return render_template("index.html", 
                           question=session["quiz"][session["current_question"]], 
                           question_number=session["current_question"] + 1)

@app.route("/result")
def result():
    return render_template("result.html", 
                           score=session["score"], 
                           total=len(session["quiz"]), 
                           wrong_answers=session["wrong_answers"])  # 传递错题信息

if __name__ == "__main__":
    app.run(debug=True)
