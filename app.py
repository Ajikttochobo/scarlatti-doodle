import gradio as gr

def dummyFuc():
    return "hello"

with gr.Blocks(title="Scarlatti Doodle") as demo:
    gr.Markdwon("hello")

if __name__ == "__main__":
    demo.launch()