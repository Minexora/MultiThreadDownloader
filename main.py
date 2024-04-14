import os
import json
import traceback
import threading
from config.config import settings
from src.balancer import DownloadBalancer


class FileOperations:

    def __init__(self):
        self.base_dir = os.path.dirname(__file__)
        self.source_file = os.path.join(self.base_dir, settings.source_file)
        self.download_path = os.path.join(
            self.base_dir,
            settings.download_path
        )
        self.combine_path = os.path.join(self.base_dir, settings.combine_path)

    def read_source(self, source):
        download_source = None
        try:
            with open(source, "r+", encoding="utf-8") as file:
                download_source = file.read()
                if download_source:
                    download_source = json.loads(download_source)['source']
        except Exception:
            print(traceback.format_exc())
        return download_source

    def get_difference_between_two_lists(self, array1, delete_dict):
        return [x for x in array1 if x != delete_dict]

    def save_source(self, source, data):
        try:
            with open(source, "w+", encoding="utf-8") as file:
                file.write(data)
        except Exception:
            print(traceback.format_exc())

    def file_control(self, delete_dict=None, check=False):
        try:
            if check:
                readed_file = self.read_source(source=self.source_file)
                delete_dict.pop('download_path', None)
                delete_dict.pop('combine_path', None)
                response_different = self.get_difference_between_two_lists(
                    readed_file,
                    delete_dict
                )
                self.save_source(
                    source=self.source_file,
                    data=json.dumps({'source': response_different}, indent=4)
                )
                return response_different
            else:
                return self.read_source(source=self.source_file)
        except Exception:
            print(traceback.format_exc())


def parse_threads(cls, dowload_list, download_path, combine_path):

    threads = []
    for _ in range(settings.number_of_downloads):
        if len(dowload_list) <= 0:
            break
        data = dowload_list.pop(0)
        thread = DownloadBalancer(
            download_url=data,
            download_path=download_path,
            combine_path=combine_path,
            thread_count=settings.number_of_threads_in_the_download
        )

        thread.name = json.dumps(data)
        threads.append(thread)
        thread.start()

    while len(threads) > 0:
        for thread in threads:
            if thread.is_alive():
                continue

            if thread.status:
                cls.file_control(
                    delete_dict=json.loads(thread.name),
                    check=True
                )
                threads.remove(thread)
            else:
                print('\n \tHATA ALINDI !\n')
                dowload_list.append(json.loads(thread.name))

            if len(dowload_list) > 0:
                new_thread = DownloadBalancer(
                    download_url=data,
                    download_path=download_path,
                    combine_path=combine_path,
                    thread_count=settings.number_of_threads_in_the_download
                )
                threads.append(new_thread)
                new_thread.start()


if __name__ == "__main__":
    cls = FileOperations()
    dowload_list = cls.file_control()
    parse_threads(
        cls=cls,
        dowload_list=dowload_list,
        download_path=cls.download_path,
        combine_path=cls.combine_path
    )

    print('Bitti :D')
