from ai.ocr import extract_text

text = extract_text("uploads/sample.jpg.jpeg")

print("===== OCR OUTPUT =====")
print(text)