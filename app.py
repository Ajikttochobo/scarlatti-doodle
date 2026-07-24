import gradio as gr

# 1. 실행할 파이썬 함수 만들기
def generate_melody_info(song_title, tempo, is_major):
    scale_type = "Major" if is_major else "Minor"
    return f"🎵 곡 제목: [{song_title}] | 설정: {tempo} BPM / {scale_type} 조성"

# 2. Gradio 인터페이스 구성하기
demo = gr.Interface(
    fn=generate_melody_info,  # 연결할 파이썬 함수
    inputs=[                  # 입력 UI 요소들
        gr.Textbox(label="곡 제목 입력", placeholder="예: Scarlatti Sonata"),
        gr.Slider(60, 180, value=120, step=1, label="템포 (BPM)"),
        gr.Checkbox(label="장조(Major) 여부", value=True)
    ],
    outputs=gr.Textbox(label="생성 결과"), # 결과 출력 UI
    title="🎹 나의 첫 Gradio 웹 앱",
    description="파이썬 함수를 웹UI로 바로 연결해주는 라이브러리입니다!"
)

# 3. 앱 실행
if __name__ == "__main__":
    demo.launch()
