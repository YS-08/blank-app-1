import os
from googleapiclient.discovery import build

# 사용자 설정
YOUTUBE_API_KEY = "YOUR_API_KEY" # 여기에 발급받은 API 키를 넣어주세요.
CHANNEL_ID = "UC3W19wZg_f22j-3c9x1W8wA" # HYBE LABELS 채널 ID
SEARCH_QUERY = "Official MV"
EXCLUDE_QUERY = "test"

# YouTube API 클라이언트 생성
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def get_video_data():
    """
    HYBE LABELS 채널에서 'Official MV' 영상을 검색하고 데이터(제목, 썸네일, 조회수)를 가져옵니다.
    """
    video_data_list = []
    next_page_token = None

    while True:
        # 영상 검색 요청
        search_response = youtube.search().list(
            channelId=CHANNEL_ID,
            q=SEARCH_QUERY,
            type='video',
            part='id,snippet',
            maxResults=50, # 한 페이지에 가져올 최대 결과 수
            pageToken=next_page_token
        ).execute()

        # 검색 결과에서 원하는 영상 정보 추출
        for item in search_response.get('items', []):
            video_id = item['id']['videoId']
            video_title = item['snippet']['title']
            
            # 'test'가 포함된 제목은 제외
            if EXCLUDE_QUERY in video_title.lower():
                continue
            
            # 영상 상세 정보 요청 (조회수를 가져오기 위해)
            video_response = youtube.videos().list(
                id=video_id,
                part='statistics,snippet'
            ).execute()
            
            # 조회수와 썸네일 추출
            for video_item in video_response.get('items', []):
                view_count = int(video_item['statistics']['viewCount'])
                thumbnail_url = video_item['snippet']['thumbnails']['high']['url']
                
                # 데이터 딕셔너리 생성
                video_data = {
                    'title': video_title,
                    'views': view_count,
                    'thumbnail': thumbnail_url
                }
                video_data_list.append(video_data)
        
        # 다음 페이지가 있는지 확인
        next_page_token = search_response.get('nextPageToken')
        if not next_page_token:
            break
            
    return video_data_list

def sort_and_print_videos(videos):
    """
    영상 데이터를 조회수 기준으로 정렬하고 출력합니다.
    """
    # 조회수 기준 내림차순 정렬
    sorted_videos = sorted(videos, key=lambda x: x['views'], reverse=True)
    
    # 순위와 함께 정보 출력
    for i, video in enumerate(sorted_videos, 1):
        print(f"--- {i}위 ---")
        print(f"제목: {video['title']}")
        print(f"조회수: {video['views']:,}회") # 쉼표로 숫자 포맷팅
        print(f"썸네일 URL: {video['thumbnail']}")
        print("-" * 20)
        
if __name__ == "__main__":
    try:
        videos = get_video_data()
        if videos:
            sort_and_print_videos(videos)
        else:
            print("조건에 맞는 영상을 찾을 수 없습니다.")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")