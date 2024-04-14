import os
import requests
import datetime
import threading

requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)


class FileDownloader:
    status = True

    def __init__(self, url, file_name, extension, file_cunk_path=None, counter=None):
        self.daemon = True
        self.url = url
        self.counter = counter
        self.file_name = file_name
        self.file_cunk_path = file_cunk_path
        self.extension = extension
        res, data = self.download()
        if not res:
            self.status = False
            print(data)
            return False
        return True

    def file_check(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def send_request(self):
        try:
            response = requests.get(self.url, stream=True, verify=False)
            return True, response
        except Exception as e:
            print("Exception request:%s" % e.args)
            return False, str(e)

    def download(self):
        print("\n\tStart downloading %s" % self.counter)
        start = datetime.datetime.now().replace(microsecond=0)

        for _ in range(10):
            is_ok, response = self.send_request()
            if is_ok:
                break
        else:
            return False, response

        file_path = f"{self.file_cunk_path}/{self.counter if self.counter is not None else self.file_name}.{self.extension}"

        try:
            self.file_check(self.file_cunk_path)
            with open(file_path, "wb+") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
        except Exception as e:
            print(str(e))
            return False, str(e)
        end = datetime.datetime.now().replace(microsecond=0)
        print("\tTime consuming: %s\n" % (end-start))

        return True, None
