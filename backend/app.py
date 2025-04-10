from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from transformers import pipeline
from newspaper import Article
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
CORS(app)

# Load summarizer
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        article = Article(url)
        article.download()
        article.parse()
        full_text = article.text

        # Split article into meaningful paragraphs (sections)
        paragraphs = [p.strip() for p in full_text.split('\n') if len(p.strip()) > 100]

        section_summaries = []
        for i, para in enumerate(paragraphs):
            summary = summarizer(para, max_length=150, min_length=20, do_sample=False)[0]['summary_text']
            section_summaries.append({
                "section": f"Section {i + 1}",
                "summary": summary
            })

        return jsonify({"sections": section_summaries})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    from textwrap import wrap

    data = request.json
    sections = data.get('sections', [])

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    text_object = p.beginText(40, height - 50)
    text_object.setFont("Helvetica", 12)
    max_chars_per_line = 90  # adjust for consistent line width

    for section in sections:
        heading = f"{section['section']}"
        summary = section['summary']

        wrapped_heading = wrap(heading, width=max_chars_per_line)
        wrapped_summary = wrap(summary, width=max_chars_per_line)

        for line in wrapped_heading:
            if text_object.getY() < 50:
                p.drawText(text_object)
                p.showPage()
                text_object = p.beginText(40, height - 50)
                text_object.setFont("Helvetica-Bold", 12)
            text_object.textLine(line)
        text_object.setFont("Helvetica", 12)
        for line in wrapped_summary:
            if text_object.getY() < 50:
                p.drawText(text_object)
                p.showPage()
                text_object = p.beginText(40, height - 50)
                text_object.setFont("Helvetica", 12)
            text_object.textLine(line)
        text_object.textLine("")

    p.drawText(text_object)
    p.showPage()
    p.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="summary.pdf", mimetype='application/pdf')



if __name__ == '__main__':
    app.run(debug=True)
