import openai
import json
import spacy
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)


nlp = spacy.load('en_core_web_sm')

with open('cleaned_pratham_data.json', 'r') as f:
    cleaned_data = json.load(f)


openai.api_key = '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'

def generate_answer(question):
    combined_content = ' '.join(item['summary'] for item in cleaned_data if 'summary' in item)
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=f"Answer the following question based on the provided context:\n\n{combined_content}\n\nQuestion: {question}\n\nAnswer:",
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5
    )
    return response.choices[0].text.strip()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    question = data.get('question')
    if not question:
        return jsonify({"error": "No question provided"}), 400

    try:
        answer = generate_answer(question)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
