import streamlit as st
import os
from googleapiclient.discovery import build

# --- 1. 설정 및 API 클라이언트 생성 ---
# 여기에 발급받은 API 키를 넣어주세요.
# Streamlit의 Secrets 기능을 사용하여 API 키를 숨길 수 있습니다.
# st.secrets['YOUTUBE_API_KEY']
YOUTUBE_API_KEY = "YOUR_API_KEY"
CHANNEL_ID = "UC3W19wZg_f22j-3c9x1W8wA"  # HYBE LABELS 채널 ID
SEARCH_QUERY = "Official MV"
EXCLUDE_QUERY = "test"

# YouTube API 클라이언트 생성
try:
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
except Exception as e:
    st.error(f"YouTube API 클라이언트를 생성하는 데 오류가 발생했습니다: {e}")
    st.stop()

# --- 2. 데이터 가져오는 함수 ---
@st.cache_data(ttl=3600)  # 1시간 동안 데이터를 캐싱
def get_video_data():
    video_data_list = []
    next_page_token = None
    
    # 로딩 상태 표시
    progress_bar = st.progress(0)
    
    while True:
        try:
            search_response = youtube.search().list(
                channelId=CHANNEL_ID,
                q=SEARCH_QUERY,
                type='video',
                part='id,snippet',
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            for item in search_response.get('items', []):
                video_title = item['snippet']['title']
                if EXCLUDE_QUERY.lower() in video_title.lower():
                    continue

                video_id = item['id']['videoId']
                video_response = youtube.videos().list(
                    id=video_id,
                    part='statistics,snippet'
                ).execute()

                for video_item in video_response.get('items', []):
                    view_count = int(video_item['statistics']['viewCount'])
                    thumbnail_url = video_item['snippet']['thumbnails']['high']['url']

                    video_data = {
                        'title': video_title,
                        'views': view_count,
                        'thumbnail': thumbnail_url
                    }
                    video_data_list.append(video_data)
            
            # 진행 상태 업데이트
            progress_bar.progress(len(video_data_list) / 1000) # 대략적인 진행률 표시 (1000개 영상 기준)
            
            next_page_token = search_response.get('nextPageToken')
            if not next_page_token:
                break
        except Exception as e:
            st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
            break
            
    return video_data_list

# --- 3. Streamlit 앱 화면 구성 ---
st.title("HYBE LABELS Official MV 조회수 순위 🏆")
st.markdown("유튜브 채널 'HYBE LABELS'의 공식 뮤직비디오 조회수 순위를 보여줍니다.")

if YOUTUBE_API_KEY == "YOUR_API_KEY":
    st.warning("API 키를 입력해 주세요. 'YOUR_API_KEY' 부분을 발급받은 키로 교체해야 합니다.")
else:
    with st.spinner('데이터를 불러오는 중입니다... 잠시만 기다려주세요.'):
        video_list = get_video_data()

    if video_list:
        # 조회수 기준 내림차순 정렬
        sorted_videos = sorted(video_list, key=lambda x: x['views'], reverse=True)

        st.success("데이터를 성공적으로 불러왔습니다!")
        st.write("---")
        
        # 순위 정보 표시
        for i, video in enumerate(sorted_videos[:20], 1): # 상위 20개만 표시
            st.subheader(f"{i}위: {video['title']}")
            st.image(video['thumbnail'], width=400)
            st.write(f"**조회수:** {video['views']:,}회")
            st.write("---")
    else:
        st.warning("데이터를 불러오지 못했거나, 조건에 맞는 영상이 없습니다. API 키를 확인해 주세요.")