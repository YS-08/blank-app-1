import streamlit as st
from googleapiclient.discovery import build
import os

# Streamlit의 Secrets 기능으로 API 키 불러오기
# secrets.toml 파일에 키를 저장해야 합니다.
try:
    YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]
except KeyError:
    st.error("API 키를 찾을 수 없습니다. '.streamlit/secrets.toml' 파일에 'YOUTUBE_API_KEY'를 설정해주세요.")
    st.stop()

# --- 사용자 설정 ---
CHANNEL_ID = "UC3W19wZg_f22j-3c9x1W8wA"  # HYBE LABELS 채널 ID
SEARCH_QUERY = "Official MV"
EXCLUDE_QUERY = "test"

# YouTube API 클라이언트 생성
@st.cache_resource
def get_youtube_client():
    try:
        return build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    except Exception as e:
        st.error(f"YouTube API 클라이언트를 생성하는 데 오류가 발생했습니다: {e}")
        st.stop()

youtube = get_youtube_client()

# --- 데이터 가져오는 함수 (캐싱 적용) ---
@st.cache_data(ttl=3600)  # 1시간 동안 데이터를 캐싱
def get_video_data():
    """
    HYBE LABELS 채널에서 'Official MV' 영상을 검색하고 데이터(제목, 썸네일, 조회수)를 가져옵니다.
    """
    video_data_list = []
    next_page_token = None
    
    # 로딩 상태 표시
    progress_text = "데이터를 불러오는 중입니다. 잠시만 기다려주세요."
    my_bar = st.progress(0, text=progress_text)
    
    total_videos = 0
    search_count = 0

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

            video_ids = [item['id']['videoId'] for item in search_response.get('items', []) if EXCLUDE_QUERY.lower() not in item['snippet']['title'].lower()]
            
            if not video_ids:
                break
                
            video_response = youtube.videos().list(
                id=','.join(video_ids),
                part='statistics,snippet'
            ).execute()

            for video_item in video_response.get('items', []):
                try:
                    view_count = int(video_item['statistics']['viewCount'])
                    thumbnail_url = video_item['snippet']['thumbnails']['high']['url']
                    video_title = video_item['snippet']['title']
                    
                    video_data = {
                        'title': video_title,
                        'views': view_count,
                        'thumbnail': thumbnail_url
                    }
                    video_data_list.append(video_data)
                except (KeyError, ValueError):
                    continue

            next_page_token = search_response.get('nextPageToken')
            
            search_count += 1
            my_bar.progress(search_count / 10, text=progress_text)  # 10번의 검색 페이지로 가정하고 진행률 표시
            
            if not next_page_token:
                break
        
        except Exception as e:
            st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
            break
            
    my_bar.empty() # 진행바 제거
    return video_data_list

# --- Streamlit 앱 화면 구성 ---
st.set_page_config(layout="wide")
st.title("HYBE LABELS Official MV 조회수 순위 🏆")
st.markdown("---")

with st.spinner('데이터를 불러오는 중입니다... 잠시만 기다려주세요.'):
    video_list = get_video_data()

if video_list:
    # 조회수 기준 내림차순 정렬
    sorted_videos = sorted(video_list, key=lambda x: x['views'], reverse=True)

    st.success("데이터를 성공적으로 불러왔습니다!")
    
    # 순위 정보 표시
    cols = st.columns(3) # 3열로 화면 분할
    
    for i, video in enumerate(sorted_videos[:30], 1): # 상위 30개 영상 표시
        col = cols[(i-1) % 3] # 열 순서 지정 (0, 1, 2, 0, 1, 2...)
        
        with col:
            st.markdown(f"### <p style='text-align: center;'>{i}위</p>", unsafe_allow_html=True)
            st.image(video['thumbnail'], use_column_width=True)
            st.markdown(f"**{video['title']}**")
            st.markdown(f"<p style='color: gray;'>조회수: {video['views']:,}회</p>", unsafe_allow_html=True)
            st.markdown("---")
else:
    st.warning("데이터를 불러오지 못했거나, 조건에 맞는 영상이 없습니다. API 키를 확인하거나 할당량을 점검해 주세요.")