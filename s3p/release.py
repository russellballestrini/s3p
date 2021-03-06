from boto.s3.key import Key
from datetime import datetime as dt
from time import time

precision_epoch = lambda: int(time()*1000)
normal_epoch = lambda x : int(x)/1000

def _make_key_path(ordered_parts):
    return '/'.join(ordered_parts)

class S3Release(object):
    """
    Represents a release (object) in an S3Pipeline.

    This class acts like boto.s3.key.Key through composition.
    """

    def __getattr__(self, attr):
        """Composition Magic: if a get attribute fails, look here next."""
        return getattr(self.key, attr)

    def __init__(self, pipeline, filepath, rank):
        self.pipeline = pipeline
        self.filepath = filepath
        self.rank = rank
        self.refresh_keys()

    def refresh_keys(self):
        """refresh self.key and self.prev_key objects with data from S3"""
        self.key = self.pipeline.get_key(self.key_path)
        self.prev_key = self.pipeline.get_key(self.prev_key_path)

    @property
    def filepath(self):
        """Get filepath of this release."""
        return self._filepath

    @filepath.setter
    def filepath(self, filepath):
        """Set filepath and filename of this release."""
        self._filepath = filepath
        self.filename  = filepath.split('/')[-1]

    @property
    def rank(self):
        """Get rank or target rank of this release."""
        return self._rank

    @rank.setter
    def rank(self, rank):
        """Set rank or target rank of this release."""
        if rank not in self.pipeline.ranks: raise Exception('invalid rank')
        self._rank = rank

    @property
    def key_path(self):
        """Get key_path of this release."""
        return _make_key_path([self.rank, self.filename])

    @property
    def uploaded_timestamp(self):
        """Get timestamp when this release was uploaded"""
        if self.key is None: return None
        return int(self.key.metadata['uploaded_timestamp'])

    @property
    def uploaded_date(self):
        """Get datetime object when this release was uploaded"""
        return dt.fromtimestamp(normal_epoch(self.uploaded_timestamp))

    @property
    def version(self):
        """Get version metadata of this release"""
        if self.key is None: return None
        return self.key.metadata.get('version', None)

    @property
    def rank_index(self):
        """Get the index integer of this release's rank"""
        return self.pipeline.ranks.index(self.rank)

    @property
    def prev_rank_index(self):
        """Get the index integer of the previous release's rank or None"""
        if self.rank_index <= 0: return None
        return self.rank_index - 1

    @property
    def prev_rank(self):
        """Get previous rank name or None"""
        if self.prev_rank_index is None: return None
        return self.pipeline.ranks[self.prev_rank_index]

    @property
    def prev_key_path(self):
        """Get previous key_path of this release or None"""
        if self.prev_rank is None: return None
        return _make_key_path([self.prev_rank, self.filename])

    @property
    def prev_version(self):
        """Get version metadata of the previous rank's release"""
        if self.prev_key is None: return None
        return self.prev_key.metadata.get('version', None)

    def archive(self):
        """Archive this release to the archive area of the pipeline."""
        archive_key_parts = ['archive', self.version, self.filename]
        self.pipeline.copy_key(self.key_path, _make_key_path(archive_key_parts))

    def upload(self, new_version=None):
        """Upload this release's filepath to the first rank and archive."""
        uploaded = precision_epoch()
        key = self.key
        if key is None: key = Key(self.pipeline, self.key_path)
        if new_version is None: new_version = uploaded
        key.set_metadata('version', new_version)
        key.set_metadata('uploaded_timestamp', uploaded)
        key.set_contents_from_filename(self.filepath)
        self.refresh_keys()
        self.archive()

    def promote(self, new_version=None):
        """
        Promote this release's filepath to target rank.

        Upload only if first rank, otherwise copy from previous.

        If the release version matches new_version do nothing.
        """
        if new_version and self.prev_version and new_version != self.prev_version:
                return '{} version {} not in {} rank'.format(
                    self.filename, new_version, self.prev_rank)
        if self.version is not None:
            if self.version == new_version or self.version == self.prev_version:
                return '{} version {} already in {} rank'.format(
                    self.filename, self.version, self.rank)
        if self.prev_rank_index is None:
            # upload a new version of the file.
            self.upload(new_version)
        else:
            # promote file from previous rank.
            self.pipeline.copy_key(self.prev_key_path, self.key_path)
            self.refresh_keys()

    def download(self, filepath):
        """Download this release's contents to filepath."""
        self.key.get_contents_to_filename(filepath)

