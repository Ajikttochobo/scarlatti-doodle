import gradio as gr
import os
import partitura as pt
import matplotlib.pyplot as plt
from midi2audio import FluidSynth
import ScarlattiMelodyModel

# ********gradio 함수들********

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
        return gr.update(visible=False), gr.update(visible=False)
    else:
        return gr.update(visible=True), gr.update(visible=True, label=os.path.basename(inputMidiFile.name), value=drawPianorollPlot(inputMidiFile)) # TODO 주석달기
        # TODO 좀 이상한거 보완하기

def onPlayButtonPress(inputMidiFile):
    return

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
            audio = gr.Audio(label="hi", interactive=False, sources=[],type="filepath")
            play_button1 = gr.Button(value="▶️ play", visible=False)
            
            with gr.Accordion(label="input midi settings",open=False):
                gr.Markdown("accordion!")

        with gr.Column():
            gr.Markdown("column2")

    # ********ui 함수들********

    input_midi_file.change(fn=onMidiFileChange, 
                           inputs=input_midi_file,
                           outputs= [play_button1, pianoroll_plot])

    play_button1.click(fn=onPlayButtonPress,
                       inputs=input_midi_file,
                       outputs=play_button1
    )



if __name__ == "__main__":
    demo.launch()