import traceback
import threading
from src.downloader.m3u8 import DownloadM3U8


class DownloadBalancer(threading.Thread):
    status = True

    def __init__(self, download_url, download_path, combine_path, thread_count):
        super(DownloadBalancer, self).__init__()
        self.daemon = True
        self.download_url = download_url
        self.download_path = download_path
        self.combine_path = combine_path
        self.thread_count = thread_count
        

    def check_file_name(self, file_name):
        try:
            check_list = ['/', '\\', '.', '\'', '"', '{', '}', '?', '']
            file_name = file_name.strip()
            for item in check_list:
                file_name = file_name.replace(item, '')
            file_name = file_name.strip()
            return file_name
        except Exception:
            self.status = False
            print(traceback.format_exc())

    def get_base_url(self, url):
        try:
            url_split_arr = url.split('/')
            return '/'.join(url_split_arr[:-1])
        except Exception:
            self.status = False
            print(traceback.format_exc())

    def run(self):
        try:
            if '.m3u8' in self.download_url['url']:
                file_name = self.check_file_name(self.download_url['file_name'])
                base_url = self.get_base_url(self.download_url['url'])
                if file_name and base_url:
                    import time
                    time.sleep(10)
                    thread = DownloadM3U8(
                        url=self.download_url['url'],
                        base_url=base_url,
                        download_path=self.download_path,
                        combine_path=self.combine_path,
                        file_name=file_name,
                        thread_count=self.thread_count
                    )
                    thread.start()
                    thread.join()
                    self.status = thread.status
                else:
                    self.status = False
                    raise ValueError(
                        f'Veriler eksik geldi.Gelen veriler: file_name : {file_name} - base_url: {base_url}')
        except Exception:
            self.status = False
            print(traceback.format_exc())
