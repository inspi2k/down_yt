import os
import sys
import shutil
import subprocess
from yt_dlp import YoutubeDL

def check_and_update_ytdlp():
    """yt-dlp가 최신 버전인지 확인하고 필요시 업데이트"""
    try:
        print("yt-dlp 버전을 확인하고 업데이트 중...")
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'yt-dlp'], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("yt-dlp가 최신 버전으로 업데이트되었습니다.")
        else:
            print(f"yt-dlp 업데이트 중 오류 발생: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("yt-dlp 업데이트 시간 초과")
    except Exception as e:
        print(f"yt-dlp 업데이트 중 오류: {str(e)}")

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
            # HTTP 403 오류 해결을 위한 옵션들
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'referer': 'https://www.youtube.com/',
            'cookiesfrombrowser': ('chrome',),  # Chrome 쿠키 사용 (선택사항)
            'extractor_retries': 3,  # 추출기 재시도 횟수
            'fragment_retries': 3,   # 프래그먼트 재시도 횟수
            'retries': 3,            # 전체 재시도 횟수
            'sleep_interval': 1,     # 요청 간 대기 시간 (초)
            'max_sleep_interval': 5, # 최대 대기 시간
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
            elif 'HTTP Error 403' in err_msg or 'Forbidden' in err_msg:
                print("HTTP 403 오류가 발생했습니다. 대안 방법으로 재시도합니다...")
                # 403 오류 해결을 위한 대안 옵션
                fallback_opts = {
                    'format': 'best',
                    'outtmpl': download_path,
                    'progress_hooks': [lambda d: print(f'다운로드 진행률: {d["_percent_str"]}')],
                    'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'referer': 'https://www.youtube.com/',
                    'extractor_retries': 5,
                    'fragment_retries': 5,
                    'retries': 5,
                    'sleep_interval': 2,
                    'max_sleep_interval': 10,
                    'no_check_certificate': True,
                    'ignoreerrors': True,
                }
                try:
                    with YoutubeDL(fallback_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        print(f"다운로드 완료: {info['title']}")
                except Exception as fallback_error:
                    print(f"대안 방법도 실패했습니다: {str(fallback_error)}")
                    print("다음 해결 방법을 시도해보세요:")
                    print("1. yt-dlp를 최신 버전으로 업데이트: pip install --upgrade yt-dlp")
                    print("2. 다른 네트워크 환경에서 시도")
                    print("3. 잠시 후 다시 시도")
                    raise
            else:
                raise
            
    except Exception as e:
        print(f"오류 발생: {str(e)}")

def main():
    print("YouTube 다운로더를 시작합니다...")
    check_and_update_ytdlp()
    print()
    
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