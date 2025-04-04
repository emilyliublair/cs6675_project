from flask import Flask, render_template, request
from vector_rag import get_pinecone_context

app = Flask(__name__)

def run_notebook(input_text):
    try:
        return get_pinecone_context(input_text)
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/", methods=["GET", "POST"])
def index():
    output_text = ""
    if request.method == "POST":
        input_text = request.form["input_text"]
        output_text = run_notebook(input_text)
    return render_template("index.html", output_text=output_text)

if __name__ == "__main__":
    app.run(debug=True)
