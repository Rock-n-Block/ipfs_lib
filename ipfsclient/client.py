from typing import Any

from requests import Session

from . import encoding, multipart


def connect(endpoint, port, base="/api/v0", headers={}, username=None, password=None):
    client = Client(
        endpoint=endpoint,
        port=port,
        base=base,
        headers=headers,
        username=username,
        password=password,
    )
    return client


class Client:
    def __init__(self, endpoint, port, base, headers, username, password):
        self.endpoint = f"{endpoint}:{port}{base}"
        self.headers = headers
        self.username = username
        self.password = password
        self.chunk_size = multipart.default_chunk_size

    def __enter__(self):
        self.open_session()
        errors = self.check_connection()
        if errors:
            raise Exception(errors)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_session()

    def close_session(self):
        self._session.close()

    def open_session(self):
        self._session = Session()
        self._session.headers.update(self.headers)
        if self.username or self.password:
            self._session.auth = (self.username, self.password)

    def check_connection(self):
        request_url = f"{self.endpoint}/id"
        try:
            response = self._session.post(request_url, timeout=5)
            if response.status_code != 200:
                return f"Could not connect to {request_url}"
        except Exception as e:
            return repr(e)

    def request(
        self,
        path: str,
        headers: dict = {},
        params: dict = {},
        data: Any = None,
        files: Any = None,
        **kwargs,
    ):
        request_url = f"{self.endpoint}{path}"

        response = self._session.post(
            url=request_url,
            headers=headers,
            params=params,
            files=files,
            data=data,
            **kwargs,
        )
        if response.status_code == 200:
            return response
        raise Exception(
            f"request failed with status code {response.status_code} and error: {response.text}"
        )

    def add(self, file, *files, **kwargs):
        """Add a file, or directory of files to IPFS.

        .. code-block:: python

            >>> with io.open('nurseryrhyme.txt', 'w', encoding='utf-8') as f:
            ...	 numbytes = f.write('Mary had a little lamb')
            >>> client.add('nurseryrhyme.txt')
            {'Hash': 'QmZfF6C9j4VtoCsTp4KSrhYH47QMd3DNXVZBKaxJdhaPab',
            'Name': 'nurseryrhyme.txt'}

        Parameters
        ----------
        file : Union[str, bytes, os.PathLike, int, io.IOBase]
            A filepath, path-object, file descriptor or open file object the
            file or directory to add
        recursive : bool
            If ``file`` is some kind of directory, controls whether files in
            subdirectories should also be added or not (Default: ``False``)
        pattern : Union[str, list]
            Single `*glob* <https://docs.python.org/3/library/glob.html>`_
            pattern or list of *glob* patterns and compiled regular expressions
            to match the names of the filepaths to keep
        trickle : bool
            Use trickle-dag format (optimized for streaming) when generating
            the dag; see `the FAQ <https://github.com/ipfs/faq/issues/218>` for
            more information (Default: ``False``)
        only_hash : bool
            Only chunk and hash, but do not write to disk (Default: ``False``)
        wrap_with_directory : bool
            Wrap files with a directory object to preserve their filename
            (Default: ``False``)
        chunker : str
            The chunking algorithm to use
        pin : bool
            Pin this object when adding (Default: ``True``)
        raw_leaves : bool
            Use raw blocks for leaf nodes. (experimental). (Default: ``True``
            when ``nocopy`` is True, or ``False`` otherwise)
        nocopy : bool
            Add the file using filestore. Implies raw-leaves. (experimental).
            (Default: ``False``)

        Returns
        -------
            Union[dict, list]
                File name and hash of the added file node, will return a list
                of one or more items unless only a single file was given
        """
        # PY2: No support for kw-only parameters after glob parameters
        recursive = kwargs.pop("recursive", False)
        pattern = kwargs.pop("pattern", "**")

        assert not isinstance(
            file, (tuple, list)
        ), "Use `client.add(name1, name2, …)` to add several items"
        multiple = len(files) > 0
        to_send = ((file,) + files) if multiple else file
        body, headers, is_dir = multipart.stream_filesystem_node(
            to_send, recursive, pattern, self.chunk_size
        )

        resp = self.request("/add", data=body, headers=headers, **kwargs).json()
        return resp.get("Hash")

    def get(self, hash: str, params: dict = {}, headers: dict = {}) -> bytes:
        params.update({"arg": hash})
        response = self.request(path="/get", params=params, headers=headers)
        return response

    def add_bytes(self, data, **kwargs):

        body, headers = multipart.stream_bytes(data, self.chunk_size)

        response = self.request(
            path="/add", data=body, headers=headers, **kwargs
        ).json()
        return response.get("Hash")

    def add_json(self, json_obj: dict = {}, **kwargs) -> str:

        return self.add_bytes(encoding.Json().encode(json_obj), **kwargs)

    def get_json(self, hash, params: dict = {}, headers: dict = {}):
        params.update({"arg": hash})
        response = self.request(path="/cat", params=params, headers=headers)
        return response.json()

    def add_str(self, string, **kwargs):

        body, headers = multipart.stream_text(string, self.chunk_size)
        response = self.request("/add", data=body, headers=headers, **kwargs).json()
        return response.get("Hash")

    def get_str(self, hash, params: dict = {}, headers: dict = {}):
        params.update({"arg": hash})
        response = self.request(path="/cat", params=params, headers=headers)
        return response.text
