from yt_dlp import YoutubeDL

def download_video(url):
    try:
        # yt-dlp 옵션 설정
        ydl_opts = {
            'format': 'bestvideo',  # 또는 'bestaudio'로 변경
            'progress_hooks': [lambda d: print(f'다운로드 진행률: {d["_percent_str"]}')],
        }
        
        # 다운로드 실행
        print("다운로드 시작...")
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            print(f"다운로드 완료: {info['title']}")
            
    except Exception as e:
        print(f"오류 발생: {str(e)}")

def main():
    while True:
        video_url = input("YouTube URL을 입력하세요 (종료하려면 'q' 입력): ")
        if video_url.lower() == 'q':
            print("프로그램을 종료합니다.")
            break
        
        if not video_url.strip():
            print("URL을 입력해주세요.")
            continue
            
        download_video(video_url)
        print("\n다음 동영상을 다운로드하시려면 새로운 URL을 입력하세요.\n")

if __name__ == "__main__":
    main() 