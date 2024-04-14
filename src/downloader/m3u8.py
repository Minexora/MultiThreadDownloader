import os
import time
import queue
import shutil
import requests
import traceback
import threading
import concurrent.futures

from src.downloader.file_downloader import FileDownloader

requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning)


class DownloadM3U8(threading.Thread):
    status = True

    def __init__(self, url, base_url, download_path, combine_path, file_name, thread_count):
        super(DownloadM3U8, self).__init__()
        self.download_path = download_path
        self.url = url
        self.base_url = base_url
        self.combine_path = combine_path
        self.file_name = file_name
        self.thread_count = thread_count
        self.file_cunk_path = f'{self.download_path}/{self.file_name}'
        self.get_urls()

    def get_urls(self):
        self.urls = {"ts": queue.Queue(), "m4s": queue.Queue()}
        try:
            r = requests.get(self.url)
            for line in r.text.split('\n'):
                if ".ts" in line:
                    self.urls['ts'].put(self.base_url + '/' + line)
                elif ".m4s" in line or ".mp4" in line:
                    if ":URI=" in line:
                        line = line.split('"')[1]
                    self.urls['m4s'].put(self.base_url + '/' + line)
        except Exception:
            self.status = False
            print(traceback.format_exc())

    def file_check(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def run(self):
        if self.urls["ts"].qsize() > 0:
            urls = self.urls["ts"]
            self.extension = "ts"
        elif self.urls["m4s"].qsize() > 0:
            urls = self.urls["m4s"]
            self.extension = "m4s"
        else:
            urls = queue.Queue()
            self.extension = None

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.thread_count) as executor:
            for i in range(urls.qsize()):
                url = urls.get()
                file_name = url.split(".ts")[0].split('-')[-1]
                future = executor.submit(
                    FileDownloader, url,
                    file_name, self.extension,
                    self.file_cunk_path, i
                )

        time.sleep(5)
        print("Conbine Start")
        self.combine()
        print("Conbine Finish")

    def file_walker(self):
        self.file_list = []
        for root, dirs, files in os.walk(self.file_cunk_path):
            # ada göre sıralayıp dosyaları düzgin şekilde birleştirmek için kullanılıyor.
            def get_key(obj):
                first_split = obj.split('.')[0]
                return int(first_split)

            files.sort(key=get_key)
            for fn in files:
                p = str(root+'/'+fn)
                self.file_list.append(p)

    def combine(self):
        self.file_walker()
        file_path = f"{self.combine_path}/{self.file_name}.{'mp4' if self.extension == 'm4s' else 'ts'}"
        self.file_check(path=self.combine_path)
        if len(self.file_list) > 0:
            with open(file_path, 'wb+') as fw:
                for i in range(len(self.file_list)):
                    fw.write(open(self.file_list[i], 'rb').read())
                    os.remove(self.file_list[i])
                shutil.rmtree(self.file_cunk_path)
