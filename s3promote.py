from os import environ

from argparse import ArgumentParser

from uuid import uuid4

from boto.s3.connection import S3Connection

from boto.s3.key import Key

def _get_filename(filepath):
    """accept a filepath, return filename"""
    return filepath.split('/')[-1]

def _key_path(ordered_parts):
    return '/'.join(ordered_parts)

class S3Promote(object):

    def __getattr__(self, attr):
        """Composition Magic: if a get attribute fails, look here next."""
        return getattr(self.bucket, attr)

    def __init__(self, **kwargs):
        """pass"""
        # if not passed, S3Connection automatically tries to use
        # env vars: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
        self.s3 = S3Connection(**kwargs)

        bucket_name = kwargs.get('bucket', environ.get('AWS_S3_BUCKET', None))
        if bucket_name == None:
            raise Exception("Pass or set a bucket name.")
        self.bucket = self.s3.get_bucket(bucket_name)

        raw_ranks = kwargs.get('ranks', environ.get('AWS_S3_RANKS', None))
        if raw_ranks == None:
            raise Exception("Pass or set some ranks.")
        # mutate into a list, split on coma and strip whitespace.
        self.ranks = [rank.strip() for rank in raw_ranks.split(',')]

    def upload(self, filepath, version=None):
        """upload a file to the first rank"""
        if version == None: version = str(uuid4())
        key_name = _key_path([self.ranks[0], _get_filename(filepath)])
        k = Key(self, key_name)
        k.set_metadata('version', version)
        k.set_contents_from_filename(filepath)

    def promote(self, filepath, new_rank, version=None):
        """promote a file in S3 through the ranks"""
        filename = _get_filename(filepath)
        self.archive(filename, new_rank)
        # new_ranks index
        i = self.ranks.index(new_rank)
        if i == 0:
            self.upload(filepath, version)
        else:
            src = _key_path([self.ranks[i-1], filename])
            dst = _key_path([self.ranks[ i ], filename])
            self.copy_key(src, dst)

    def archive(self, filename, rank):
        """move file if it exists to archive area with version"""
        key = self.get_key(_key_path([rank, filename]))
        if key != None:
            version = key.metadata['version']
            key.copy(self, _key_path(['archive', version, filename]))

    def copy_key(self, src, dst):
        """copy file in S3 to a new key name"""
        return self.bucket.copy_key(dst, self.name, src)


if __name__ == '__main__':
    parser = ArgumentParser("promote a file through the ranks")
    parser.add_argument('filepath')
    parser.add_argument('new_rank')
    parser.add_argument('-v', '--version', help='optional unique identifier', default=None)
    args = parser.parse_args()

    promoter = S3Promote()

    if args.new_rank not in promoter.ranks:
        print('error="invalid rank"')
        exit(2)

    result = promoter.promote(args.filepath, args.new_rank, args.version)

    if result == False:
        print('error="could not promote, trying to skip rank?"')
        exit(2)

    print('success="promoted {} to {}"'.format(args.filepath,args.new_rank))
