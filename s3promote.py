from os import environ

from argparse import ArgumentParser

from uuid import uuid4

from boto.s3.connection import S3Connection

from boto.s3.key import Key

def _make_key_path(ordered_parts):
    return '/'.join(ordered_parts)

class S3Pipeline(object):
    """
    Represents a release pipeline (object) in S3.

    This class acts like boto.s3.bucket.Bucket through composition.
    """

    def __getattr__(self, attr):
        """Composition Magic: if a get attribute fails, look here next."""
        return getattr(self.bucket, attr)

    def __init__(self, **kwargs):
        """Build the pipeline object with keyword args or env vars."""
        # if not passed, S3Connection automatically tries to use
        # env vars: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
        self.s3 = S3Connection(**kwargs)

        bucket_name = kwargs.get('bucket', environ.get('AWS_S3_BUCKET', None))
        if bucket_name == None:
            raise Exception("Pass or set a bucket name.")
        try:
            self.bucket = self.s3.get_bucket(bucket_name)
        except:
            # boto.exception.S3ResponseError: S3ResponseError: 404 Not Found
            self.bucket = self.s3.create_bucket(bucket_name)

        raw_ranks = kwargs.get('ranks', environ.get('AWS_S3_RANKS', None))
        if raw_ranks == None:
            raise Exception("Pass or set some ranks.")
        # mutate into a list, split on coma and strip whitespace.
        self.ranks = [rank.strip() for rank in raw_ranks.split(',')]

    def get_release(self, filepath, rank):
        """Return an S3Release object for filepath and rank"""
        return S3Release(self, filepath, rank)

    def get_releases(self, filepath):
        """Return a list of releases of a filepath in the pipeline."""
        return [self.get_release(filepath, rank) for rank in self.ranks]

    def file_info(self, filepath):
        """TODO: is this silly? Return pipeline data about file in all ranks"""
        data = {}
        for release in self.get_releases(filepath):
            rank = release.rank
            data[rank] = release.metadata
            data[rank]['name'] = release.name
            data[rank]['filename'] = release.filename
            data[rank]['size'] = release.size
            data[rank]['etag'] = release.etag.strip('"')
            data[rank]['md5'] = release.md5
            data[rank]['last_modified'] = release.last_modified
            data[rank]['version'] = release.version
            data[rank]['content_type'] = release.content_type
            data[rank]['content_encoding'] = release.content_encoding
        return data

    def file_versions(self, filepath):
        versions = []
        for release in self.get_releases(filepath):
            versions.append((release.name,release.version))
        return versions

    def copy_key(self, src_key_path, dst_key_path):
        """Copy src_key_path to dst_key_path """
        return self.bucket.copy_key(dst_key_path,self.bucket.name,src_key_path)


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

    @property
    def key(self):
        """Always fresh view of key object."""
        return self.pipeline.get_key(self.key_path)

    @property
    def prev_key(self):
        """Always fresh view of prev_key object."""
        return self.pipeline.get_key(self.prev_key_path)

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
    def version(self):
        """Get version metadata of this release"""
        if self.key == None: return None
        return self.key.metadata['version']

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
    def prev_key_path(self):
        """Get previous key_path of this release or None"""
        if self.prev_rank_index == None: return None
        return _make_key_path([self.pipeline.ranks[self.prev_rank_index], self.filename])

    @property
    def prev_version(self):
        """Get version metadata of the previous rank's release"""
        if self.prev_key == None: return None
        return self.prev_key.metadata['version']

    def archive(self):
        """Archive this release to the archive area of the pipeline."""
        archive_key_parts = ['archive', self.version, self.filename]
        self.pipeline.copy_key(self.key_path, _make_key_path(archive_key_parts))

    def upload(self, new_version=None):
        """Upload this release's filepath to the first rank and archive."""
        key = self.key
        if key == None: key = Key(self.pipeline, self.key_path)
        if new_version == None: new_version = str(uuid4())
        key.set_metadata('version', new_version)
        key.set_contents_from_filename(self.filepath)
        self.archive()

    def promote(self, new_version=None):
        """
        Promote this release's filepath to target rank.

        Upload only if first rank, otherwise copy from previous.

        If the release version matches new_version do nothing.
        """
        if self.version != None:
            if self.version == new_version or self.version == self.prev_version:
                return '{} version {} already in {} rank'.format(
                    self.filename, self.version, self.rank)
        if self.prev_rank_index == None:
            # upload a new version of the file.
            self.upload(new_version)
        else:
            # promote file from previous rank.
            self.pipeline.copy_key(self.prev_key_path, self.key_path)

    def download(self, filepath):
        """Download this release's contents to filepath."""
        self.key.get_contents_to_filename(filepath)


if __name__ == '__main__':
    parser = ArgumentParser( usage='%(prog)s filepath rank',
        description="Promote files through the release ranks")
    parser.add_argument('filepath')
    parser.add_argument('rank')
    parser.add_argument('--version', default=None,
        help='set version identifier, timestamp, md5, commit hash, etc')
    parser.add_argument('--download', metavar='PATH', dest='download_path',
        default=None, help='download file from rank to PATH')
    parser.add_argument('--get-version', action='store_true', default=False,
        help='get version identifier from rank')
    parser.add_argument('--get-versions', action='store_true', default=False,
        help='get version identifier for all rank')
    parser.add_argument('--info', action='store_true', default=False,
        help='get info about release in pipeline')
    args = parser.parse_args()

    # pipeline is a Bucket like object.
    pipeline = S3Pipeline()

    if args.info == True:
        print(pipeline.file_info(args.filepath))
        exit()

    if args.get_versions == True:
        versions = pipeline.file_versions(args.filepath)
        for version in versions:
            print('{}="{}"'.format(*version))
        exit()

    # release is a Key like object.
    #release = pipeline.get_release(args.filepath, args.rank)
    try:
        release = pipeline.prepare_release(args.filepath, args.rank)
    except:
        print('error="invalid rank"')
        exit(2)

    if args.get_version == True:
        print('{}="{}"'.format(release.rank,release.version))
        exit()

    if args.download_path != None:
        release.download(args.download_path)
        exit()

    #result = release.promote(args.version)
    try:
        result = release.promote(args.version)
    except:
        print('error="could not promote, trying to skip rank?"')
        exit(2)

    if result == None:
        print('success="promoted {} version {} to {} rank"'.format(
            release.filename, release.version, release.rank))
    else:
        print('warning="{}"'.format(result))
