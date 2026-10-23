import gradio as gr
import base64
from pathlib import Path
from rag import ask, get_collection

# بناء الفهرس عند بدء التشغيل
get_collection()

# دالة لقراءة الصور وتحويلها لـ base64
def get_base64_image(image_names):
    if isinstance(image_names, str):
        image_names = [image_names]
        
    for name in image_names:
        path = Path(name)
        if path.exists():
            encoded = base64.b64encode(path.read_bytes()).decode()
            ext = path.suffix.lower().replace(".", "")
            if ext in ["jpg", "jpeg"]:
                ext = "jpeg"
            return f"data:image/{ext};base64,{encoded}"
    return ""

logo_base64 = get_base64_image(["logo.png", "الشعار.png", "logo.jpg", "الشعار.jpg"])
college_base64 = get_base64_image(["college.jpg", "الكليه.jpg", "college.png", "الكلية.jpg"])

# CSS: تقسيم الصفحة لترك مبنى الكلية ظاهراً بالكامل على اليسار
custom_css = """
body, .gradio-container {
    background-image: url('COLLEGE_BG');
    background-size: cover;
    background-position: left center; /* تركيز خلفية الكلية جهة اليسار */
    background-attachment: fixed;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 0;
}

#split-layout {
    display: flex;
    min-height: 100vh;
    align-items: center;
}

#right-panel {
    background: rgba(255, 255, 255, 0.75) !important; /* شفافية ناعمة لتناسق العناصر */
    backdrop-filter: blur(8px) !important;
    -webkit-backdrop-filter: blur(8px) !important;
    padding: 30px 35px !important;
    border-radius: 20px !important;
    box-shadow: -10px 0 30px rgba(0, 0, 0, 0.25) !important;
    border-top: 6px solid #15803d !important;
    margin: 20px 40px 20px auto !important; /* إزاحة الواجهة لليمين */
    max-width: 520px !important;
    width: 100% !important;
}

.header-container {
    text-align: center;
    margin-bottom: 15px;
}

.header-logo {
    width: 100px;
    margin: 0 auto 8px auto;
    display: block;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.15));
}

h1 {
    color: #14532d !important;
    font-weight: 800;
    font-size: 1.4rem !important;
    margin-bottom: 6px;
    text-align: center;
}

.disclaimer-text {
    color: #1f2937;
    font-size: 0.8em;
    background-color: rgba(240, 253, 244, 0.95);
    border: 1px solid #bbf7d0;
    padding: 8px 12px;
    border-radius: 8px;
    margin-top: 8px;
    display: inline-block;
    line-height: 1.4;
}

button.primary {
    background-color: #15803d !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

button.primary:hover {
    background-color: #166534 !important;
}

.secondary-btn {
    border-radius: 8px !important;
}

label span {
    color: #0f172a !important;
    font-weight: 700 !important;
}
""".replace('COLLEGE_BG', college_base64)

with gr.Blocks(css=custom_css, title="Hebron University Student Guide") as demo:
    with gr.Row(elem_id="split-layout"):
        # العمود الأيمن يحتوي التطبيق
        with gr.Column(elem_id="right-panel"):
            with gr.Column(elem_classes="header-container"):
                gr.HTML(f"<img src='{logo_base64}' class='header-logo' alt='Hebron University Logo'>")
                gr.Markdown("# Hebron University Student Guide")
                gr.Markdown(
                    "<div class='disclaimer-text'>"
                    "⚠️ <b>Note:</b> This application is a technical demonstration of Retrieval-Augmented Generation (RAG) concepts and does not represent the official reference for Hebron University."
                    "</div>"
                )
            
            question_input = gr.Textbox(
                label="Your Question / سؤالك", 
                placeholder="Enter your question here (e.g., شروط مشروع التخرج)...", 
                lines=2
            )
            
            with gr.Row():
                submit_btn = gr.Button("Submit / إرسال", variant="primary")
                clear_btn = gr.Button("Clear / مسح", elem_classes="secondary-btn")
                flag_btn = gr.Button("Flag / إبلاغ", elem_classes="secondary-btn")
                    
            answer_output = gr.Textbox(label="Answer / الإجابة", lines=4)
            source_output = gr.Textbox(label="Sources / المصدر", lines=1)

            def process_query(question):
                ans, sources = ask(question)
                src_str = ", ".join(sources) if sources else "None"
                return ans, src_str

            submit_btn.click(
                fn=process_query, 
                inputs=[question_input], 
                outputs=[answer_output, source_output]
            )
            
            clear_btn.click(
                fn=lambda: ("", "", ""), 
                inputs=None, 
                outputs=[question_input, answer_output, source_output]
            )

if __name__ == "__main__":
    demo.launch(server_port=7860)