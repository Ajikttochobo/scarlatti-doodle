import gradio as gr

# 1. 처리할 파이썬 함수 정의
def process_midi_file(midi_file, note_shift):
    if midi_file is None:
        return "⚠️ MIDI 파일을 업로드해주세요!"
    
    # file_obj.name을 사용하면 실제 저장된 파일 경로(문자열)를 얻습니다.
    file_path = midi_file.name
    return f"🎵 파일이 성공적으로 수신되었습니다!\n- 파일 경로: {file_path}\n- 옥타브/음높이 조절: {note_shift}"


# 2. gr.Blocks를 사용한 화면 조립
with gr.Blocks(title="Scarlatti Doodle") as demo:
    
    # 자유로운 텍스트 배치 (Markdown 지원)
    gr.Markdown("# 🎹 Scarlatti Doodle")
    gr.Markdown("스카를라티 스타일의 음악 분석 및 처리를 위한 대시보드입니다.")
    
    gr.Markdown("---") # 구분선 추가
    
    # Row, Column을 활용한 자유로운 화면 레이아웃 (2열 구성)
    with gr.Row():
        
        # 왼쪽 컬럼: 입력 요소들
        with gr.Column():
            gr.Markdown("### 📥 1. 데이터 입력")
            
            # MIDI 파일 받기 (label 사용)
            file_input = gr.File(
                label="MIDI 파일 선택", 
                file_types=[".mid", ".midi"]
            )
            
            # 입력 옵션 슬라이더
            shift_input = gr.Slider(
                minimum=-12, 
                maximum=12, 
                value=0, 
                step=1, 
                label="음높이 조절 (Semiteones)"
            )
            
            # 내가 직접 만드는 커스텀 실행 버튼! (Clear, Flag 버튼 없음)
            run_button = gr.Button("🎼 음악 분석 및 변환 시작", variant="primary")
            
        # 오른쪽 컬럼: 출력 요소들
        with gr.Column():
            gr.Markdown("### 📤 2. 분석 결과")
            
            # 결과 표시용 텍스트 상자
            output_box = gr.Textbox(label="실행 상태 및 결과", lines=5)

    # 3. 버튼 클릭 이벤트 연결 (클릭 시 실행될 함수, 입력 컴포넌트, 출력 컴포넌트 지정)
    run_button.click(
        fn=process_midi_file,
        inputs=[file_input, shift_input],
        outputs=output_box
    )


# 4. 앱 실행
if __name__ == "__main__":
    demo.launch()
