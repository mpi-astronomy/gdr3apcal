""" Simplified access to storage """
import os
from .downloader import download_file


class BaseRepository:
    """ Base class for downloading from specific locations """
    def __init__(self, repo: str, **kwargs):
        self.repo = repo
        self.kwargs = kwargs

    def download_file(self, fname: str, where: str):
        raise NotImplementedError

class HTTP(BaseRepository):
    """ Direct download from URL {repo}/{filename} """
    def download_file(self, fname: str, where: str):
        url = '{repo:s}/{filename:s}'.format(repo=self.repo, filename=fname)
        download_file(url, os.path.join(where, fname))


class Keeper(BaseRepository):
    """ Make a simplified interface to a folder on Keeper/Seafile """
    def download_file(self, fname: str, where: str):
        url = '{repo:s}/files/?p=%2F{filename:s}&dl=1'.format(repo=self.repo, filename=fname)
        download_file(url, os.path.join(where, fname))


registered_repositories = {'keeper': Keeper, 'http': HTTP}