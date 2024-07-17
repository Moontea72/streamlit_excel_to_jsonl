import pandas as pd
import json
import streamlit as st
from io import BytesIO

# 엑셀 파일을 JSON 파일로 변환하는 함수
def excel_to_json(excel_bytes):
    # 엑셀 파일 읽기
    df = pd.read_excel(BytesIO(excel_bytes))
    print("파일을 불러왔습니다.")
    
    # JSON 형식으로 변환
    json_bytes = df.to_json(orient='records', force_ascii=False, indent=4).encode('utf-8')
    print('JSON 파일이 저장되었습니다.')
    return json_bytes

# 엑셀 파일을 JSONL 파일로 변환하는 함수
def excel_to_jsonl(excel_bytes):
    # 엑셀 파일 읽기
    df = pd.read_excel(BytesIO(excel_bytes))
    print("파일을 불러왔습니다.")
    
    # 엑셀 파일의 header가 올바른지 검증
    if not all(col in df.columns for col in ['system', 'user', 'assistant']):
        st.error("Excel 파일의 header를 확인하세요.\n\nsystem, user, assistant 로 구성되어야 합니다.")
        return None
    
    # Fine-tuning을 위한 JSON 형식으로 변환
    json_list = []
    
    for _, row in df.iterrows():
        message = {
            "messages": [
                {"role": "system", "content": row["system"]},
                {"role": "user", "content": row["user"]},
                {"role": "assistant", "content": row["assistant"]}
            ]
        }
        json_list.append(json.dumps(message, ensure_ascii=False))
        
    # 변환된 JSON list를 최종 JSONL 파일로 변환
    jsonl_bytes = '\n'.join(json_list).encode('utf-8')
    print("JSONL 파일이 저장되었습니다.")
    return jsonl_bytes

# JSONL 파일의 유효성을 검사하는 함수
def validate_jsonl(jsonl_bytes):
    valid = True
    for line in jsonl_bytes.decode('utf-8').split('\n'):
        try:
            json.loads(line)
        except json.JSONDecodeError:
            valid = False
            break
    if valid:
        st.success("JSONL 파일이 유효합니다.")
    else:
        st.error("JSONL 파일에 오류가 존재합니다.")

st.title('⯌ Excel to JSON / L Converter :sunglasses:⯌')

st.title('_Excel File_ :orange[Upload...▼]')

uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is not None:
    # 파일 확장자 확인
    if uploaded_file.name.endswith('.xlsx'):
        bytes_data = uploaded_file.getvalue()
        file_name = uploaded_file.name.split('.')[0]  # 파일명 추출 (확장자 제거)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button('JSONL 변환'):
                jsonl_bytes = excel_to_jsonl(bytes_data)
                if jsonl_bytes:
                    validate_jsonl(jsonl_bytes)
                    st.download_button(
                        label="Download JSONL",
                        data=jsonl_bytes,
                        file_name=f'{file_name}_converted.jsonl',
                        mime='application/json'
                    )
        with col2:
            if st.button('JSON 변환'):
                json_bytes = excel_to_json(bytes_data)
                st.download_button(
                    label="Download JSON",
                    data=json_bytes,
                    file_name=f'{file_name}_converted.json',
                    mime='application/json'
                )
    else:
        st.error("업로드된 파일이 .xlsx 형식이 아닙니다. .xlsx 파일을 업로드 해주세요.")
