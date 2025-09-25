import os
import sys
import shutil
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

        # 기본: macOS/Linux는 기존 동작 유지 (최고 화질 병합 전제)
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': download_path,
            'progress_hooks': [lambda d: print(f'다운로드 진행률: {d["_percent_str"]}')],
        }

        if sys.platform == 'win32':
            # Windows에서만 ffmpeg 경로를 명시적으로 지정하고, 없으면 병합이 필요 없는 단일(progressive) 스트림만 선택
            ffmpeg_candidates = [
                shutil.which('ffmpeg.exe'),
                os.path.join(os.environ.get('PROGRAMFILES', ''), 'ffmpeg', 'bin', 'ffmpeg.exe'),
                os.path.join(os.environ.get('PROGRAMFILES', ''), 'FFmpeg', 'bin', 'ffmpeg.exe'),
                os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'ffmpeg', 'bin', 'ffmpeg.exe'),
                os.path.join('C:\\', 'ffmpeg', 'bin', 'ffmpeg.exe'),
                os.path.join(os.environ.get('ProgramData', ''), 'chocolatey', 'bin', 'ffmpeg.exe'),
            ]
            ffmpeg_path = next((p for p in ffmpeg_candidates if p and os.path.isfile(p)), None)

            if ffmpeg_path:
                ydl_opts['ffmpeg_location'] = os.path.dirname(ffmpeg_path)
                ydl_opts['merge_output_format'] = 'mp4'
            else:
                print("알림: Windows에서 ffmpeg를 찾지 못했습니다. 병합 없이 단일 스트림으로 다운로드합니다.")
                # 병합(+)이 전혀 없는 포맷 체인: 음성이 포함된 단일 스트림만 선택
                # 가능한 경우 mp4 우선 → 그 외 오디오 포함 best → 최후엔 best
                ydl_opts['format'] = (
                    'best[ext=mp4][acodec!=none]/'
                    'best[acodec!=none]/'
                    'best'
                )
        
        # 다운로드 실행
        print("다운로드 시작...")
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                print(f"다운로드 완료: {info['title']}")
        except Exception as first_error:
            err_msg = str(first_error)
            if 'Requested format is not available' in err_msg:
                print("요청한 포맷이 없어 'best' 포맷으로 한 번 더 시도합니다...")
                # 포맷을 더 보편적인 값으로 재시도
                retry_opts = dict(ydl_opts)
                if sys.platform == 'win32' and 'ffmpeg_location' not in retry_opts:
                    # ffmpeg가 없으면 병합 없는 단일 스트림으로만 재시도
                    retry_opts['format'] = 'best[ext=mp4][acodec!=none]/best[acodec!=none]/best'
                else:
                    retry_opts['format'] = 'best'
                with YoutubeDL(retry_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    print(f"다운로드 완료: {info['title']}")
            else:
                raise
            
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