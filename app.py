import gradio as gr
import os
import partitura as pt
import matplotlib.pyplot as plt
from midi2audio import FluidSynth
import ScarlattiMelodyModel

# ********gradio 함수들********

sampleFile = "In My Life.MID"

def drawPianorollPlot(score):
    note_array = pt.load_performance_midi(score).note_array() # midi 파일을 partitura performance 객체로 변환

    pitches = note_array['pitch'] 
    onsets = note_array['onset_sec']
    durations = note_array['duration_sec'] # 음 피치, 시작시간, 지속시간 값 가져옴

    fig, ax = plt.subplots(figsize=(10, 4)) # 그래프가 그려지는 전체 도화지인 figure와 실제 그래프 축인 그래프 공간을 동시에 생성하고 figure의 크기를 가로세로 10인치, 4인치의 비율로 설정
    for o, d, p in zip(onsets, durations, pitches): # 한 음당 피치 시작시간 지속시간에 접근
        ax.add_patch(plt.Rectangle((o, p - 0.4), d, 0.8, color='mediumpurple')) # 그래프에 직사각형 추가 (인자는 각각 xy튜플로, width, height, 색)

    if len(pitches) > 0:
        ax.set_ylim(min(pitches) - 2, max(pitches) + 2) # y축 최소 최대 지정
        ax.set_xlim(0, (onsets + durations).max()) # x축 최소 최대 지정

    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    return fig

def onMidiFileChange(inputMidiFile):
    if(inputMidiFile == None):
        return gr.update(visible=True), gr.update(visible=True), gr.update(visible=False)
    else:
        return gr.update(visible=True, label=os.path.basename(inputMidiFile.name), value=drawPianorollPlot(inputMidiFile)), gr.update(visible=True, value=midiToAudio(inputMidiFile)), gr.update(visible=True)

def midiToAudio(inputMidiFile):
    output_wav = "output.wav"
    FluidSynth().midi_to_audio(inputMidiFile if type(inputMidiFile) == str else inputMidiFile.name, output_wav)

    return output_wav

def onGenerateButtonPressed(inputMidiFile):
    outputMidi = ScarlattiMelodyModel.runModel(inputMidi=inputMidiFile)
    return gr.update(visible=True, value=outputMidi), gr.update(visible=True, value=drawPianorollPlot(outputMidi)), gr.update(visible=True, value=midiToAudio(outputMidi)), gr.update(visible=True)

def onResetButtonPressed():
     return gr.update(value=None), gr.update(value=None), gr.update(value=None), gr.update(value=None), gr.update(value=None), gr.update(value=None), gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), gr.update(visible=True)

def onSampleFileButtonPressed():
     return gr.update(value=sampleFile), gr.update(visible=False), gr.update(visible=False)

#********gradio 인터페이스 코드********

with gr.Blocks(title="Scarlatti Doodle") as demo:
    gr.Markdown("# Scarlatti Doodle")
    gr.Markdown("Google Bach doodle but it's Scarlatti")

    with gr.Accordion(label="About this project", open=False):
                    gr.Markdown("accordion!")
    
    gr.Markdown("---")

    with gr.Row():

        with gr.Column():
            gr.Markdown("input")
            input_midi_file = gr.File(file_types= [".midi", ".mid"], label="upload midi file")

            pianoroll_plot = gr.Plot()
            audio1 = gr.Audio(label=None, interactive=False, sources=[],type="filepath")

            sampleMarkdown =  gr.Markdown("Don't feel like uploading a file? Try it out with sample file!")
            with gr.Row():
                with gr.Column(scale=0, min_width=200):
                    sampleFileButton = gr.Button("try with sample file", variant="link", scale=0, min_width=0)


            generateButton = gr.Button(value="Generate", variant="primary", visible=False)

                 

        with gr.Column():
            gr.Markdown("result")
            output_midi_file = gr.File(label=None, interactive=False, type="filepath")
            output_pianoroll_plot = gr.Plot(visible=False)
            audio2 = gr.Audio(label=None, interactive=False, sources=[], type="filepath")
            resetButton = gr.Button(value="Reset", variant="secondary", visible=False)



    # ********ui 함수들********

    input_midi_file.change(fn=onMidiFileChange, 
                           inputs=input_midi_file,
                           outputs= [pianoroll_plot, audio1, generateButton])

    generateButton.click(fn=onGenerateButtonPressed,
                         inputs=input_midi_file,
                         outputs=[output_midi_file, output_pianoroll_plot, audio2, resetButton]
                         )

    resetButton.click(fn = onResetButtonPressed,
                      inputs = None,
                      outputs = [input_midi_file, pianoroll_plot, audio1, output_midi_file, output_pianoroll_plot, audio2, resetButton, generateButton, sampleMarkdown, sampleFileButton]
                      )

    sampleFileButton.click(fn = onSampleFileButtonPressed,
                           inputs = None,
                           outputs = [input_midi_file, sampleFileButton, sampleMarkdown])



if __name__ == "__main__":
    demo.launch()