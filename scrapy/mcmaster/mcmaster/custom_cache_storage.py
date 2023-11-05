import hashlib
import re
from time import time
from scrapy.extensions.httpcache import FilesystemCacheStorage
from pathlib import Path
import pickle
from scrapy.utils.python import to_bytes
from w3lib.http import headers_dict_to_raw, headers_raw_to_dict
from scrapy.responsetypes import responsetypes
from scrapy.http import Headers

class CustomCacheStorage(FilesystemCacheStorage):
    def __init__(self, settings):
        super().__init__(settings)
        self.dynamic_part_pattern = r'mv\d+'  # Replace with the actual dynamic part pattern

    def _replace_dynamic_part(self, url):
        return re.sub(self.dynamic_part_pattern, 'mv1698769766', url)

    def _get_request_key(self, request):
        url = self._replace_dynamic_part(request.url)
        return hashlib.sha1(url.encode('utf8')).hexdigest()

    def retrieve_response(self, spider, request):
        # modify the request url to replace the dynamic part
        request = request.replace(url=self._replace_dynamic_part(request.url))
        # print('------- RETRIEVE RESPONSE -------')
        # print(request)
        # print('---------------------------------')
        metadata = self._read_meta(spider, request)
        if metadata is None:
            return  # not cached
        rpath = Path(self._get_request_path(spider, request))
        with self._open(rpath / "response_body", "rb") as f:
            body = f.read()
        with self._open(rpath / "response_headers", "rb") as f:
            rawheaders = f.read()
        url = metadata.get("response_url")
        status = metadata["status"]
        headers = Headers(headers_raw_to_dict(rawheaders))
        respcls = responsetypes.from_args(headers=headers, url=url, body=body)
        response = respcls(url=url, headers=headers, status=status, body=body)
        return response

    def store_response(self, spider, request, response):
        request = request.replace(url=self._replace_dynamic_part(request.url))
        # print('------- STORE RESPONSE -------')
        # print(request)
        # print('---------------------------------')
        rpath = Path(self._get_request_path(spider, request))
        if not rpath.exists():
            rpath.mkdir(parents=True)
        metadata = {
            "url": request.url,
            "method": request.method,
            "status": response.status,
            "response_url": response.url,
            "timestamp": time(),
        }
        with self._open(rpath / "meta", "wb") as f:
            f.write(to_bytes(repr(metadata)))
        with self._open(rpath / "pickled_meta", "wb") as f:
            pickle.dump(metadata, f, protocol=4)
        with self._open(rpath / "response_headers", "wb") as f:
            f.write(headers_dict_to_raw(response.headers))
        with self._open(rpath / "response_body", "wb") as f:
            f.write(response.body)
        with self._open(rpath / "request_headers", "wb") as f:
            f.write(headers_dict_to_raw(request.headers))
        with self._open(rpath / "request_body", "wb") as f:
            f.write(request.body)

