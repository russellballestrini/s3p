from os import environ

from argparse import ArgumentParser

from uuid import uuid4

from boto.s3.connection import S3Connection

from boto.s3.key import Key

def _get_filename(filepath):
    """accept a filepath, return filename"""
    return filepath.split('/')[-1]

def _make_key_path(ordered_parts):
    return '/'.join(ordered_parts)

class S3Promote(object):

    #def __getattr__(self, attr):
    #    """Composition Magic: if a get attribute fails, look here next."""
    #    return getattr(self.bucket, attr)

    def __init__(self, **kwargs):
        """S3Promote bucket that builds a release pipeline with code"""
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

        if 'filepath' in kwargs:
            # invoke filepath.setter
            self.filepath = kwargs['filepath']

        if 'rank' in kwargs:
            # invoke rank.setter
            self.rank = kwargs['rank']

    @property
    def filepath(self):
        """Get filepath of subject."""
        return self._filepath

    @filepath.setter
    def filepath(self, filepath):
        """Set filepath and filename of subject."""
        self._filepath = filepath
        self.filename = _get_filename(self._filepath)

    @property
    def rank(self):
        """Get rank or target rank of subject."""
        return self._rank

    @rank.setter
    def rank(self, rank):
        """Set rank or target rank of subject."""
        if rank not in self.ranks:
            raise Exception('invalid rank')
        self._rank = rank

    @property
    def key_path(self):
        """Get key_name path of subject."""
        return _make_key_path([self.rank, self.filename])

    def get_key(self):
        """Get Key object of subject."""
        return self.bucket.get_key(self.key_path)

    @property
    def version(self):
        """Get version metadata of subject"""
        key = self.get_key()
        if key == None:
            return None
        return key.metadata['version']

    def upload(self, new_version=None):
        """Upload subject filepath to the first rank"""
        if new_version == None: new_version = str(uuid4())
        k = Key(self.bucket, self.key_path)
        k.set_metadata('version', new_version)
        k.set_contents_from_filename(self.filepath)

    def promote(self, new_version=None):
        """Archive then promote subject filepath to target rank"""
        # archive key if it exists.
        self.archive()

        # get index of target rank
        i = self.ranks.index(self.rank)

        if i == 0:
            # upload a new version of the file.
            self.upload(new_version)
        else:
            # promote file from previous rank.
            src = _make_key_path([self.ranks[i-1], self.filename])
            dst = self.key_path
            self.copy_key(src, dst)

    def archive(self):
        """Move key if it exists to archive area with version"""
        key = self.get_key()
        if key != None:
            archive_key_parts = ['archive', self.version, self.filename]
            key.copy(self.bucket, _make_key_path(archive_key_parts) )

    def copy_key(self, src_key_path, dst_key_path):
        """Copy src key_path to dst key_path """
        return self.bucket.copy_key(dst_key_path,self.bucket.name,src_key_path)


if __name__ == '__main__':
    parser = ArgumentParser("Promote files through the release ranks.")
    parser.add_argument('filepath')
    parser.add_argument('rank')
    parser.add_argument('--version', default=None,
        help='set version identifier, timestamp, md5, commit hash, etc')
    parser.add_argument('--get-version', action='store_true', default=False,
        help='get version identifier from rank')
    args = parser.parse_args()

    promoter = S3Promote()

    # set subject's filepath (and filename)
    promoter.filepath = args.filepath

    try:
        # set subject rank or target rank
        promoter.rank = args.rank
    except:
        print('error="invalid rank"')
        exit(2)

    if args.get_version == True:
        print('version="{}"'.format(promoter.version))
        exit()

    try:
        promoter.promote(args.version)
    except:
        print('error="could not promote, trying to skip rank?"')
        exit(2)

    print('success="promoted {} version {} to {} "'.format(
        promoter.filename, promoter.version, promoter.rank))
