import gradio as gr
import ScarlattiMelodyModel

# ********gradio 함수들********

def onMidiFileChange(inputMidiFile):
    if(inputMidiFile == None):
        return gr.update(visible=False), gr.update(visible=False)
    else:
        return gr.update(visible=True), gr.update(visible=True)

#********gradio 인터페이스 코드********

with gr.Blocks(title="Scarlatti Doodle") as demo:
    gr.Markdown("# Scarlatti Doodle")
    gr.Markdown("Google Bach doodle but it's Scarlatti")

    gr.Markdown("---")

    with gr.Row():

        with gr.Column():
            gr.Markdown("column1")
            input_midi_file = gr.File(file_types= [".midi", ".mid"], label="upload midi file")

            pianoroll_plot = gr.Plot(visible=False)
            play_button = gr.Button(value="▶️ play", visible=False)
            
            with gr.Accordion(label="input midi settings",open=False):
                gr.Markdown("accordion!")

        with gr.Column():
            gr.Markdown("column2")

    # ********ui 함수들********

    input_midi_file.change(fn=onMidiFileChange, 
                           inputs=input_midi_file,
                           outputs= [play_button, pianoroll_plot])



if __name__ == "__main__":
    demo.launch()