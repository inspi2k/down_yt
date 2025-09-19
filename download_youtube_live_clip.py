import os
import sys
from yt_dlp import YoutubeDL

def download_video(url):
    try:
        # yt-dlp 옵션 설정
        if sys.platform == 'darwin':  # macOS
            download_path = os.path.expanduser('~/Movies/%(title)s.%(ext)s')
        elif sys.platform == 'win32':  # Windows
            download_path = os.path.join(os.environ['USERPROFILE'], 'Videos', '%(title)s.%(ext)s')
        else:  # Other OS (e.g., Linux)
            download_path = os.path.expanduser('~/Videos/%(title)s.%(ext)s')

        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # 최고 화질 비디오와 오디오를 병합하여 다운로드, 또는 가능한 최고 화질
            'outtmpl': download_path,  # 다운로드 경로 설정
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