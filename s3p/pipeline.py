from os import environ
from boto.s3.connection import S3Connection
from release import S3Release

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
            data[rank]['uploaded_date'] = release.uploaded_date
            data[rank]['last_modified'] = release.last_modified
            data[rank]['content_type'] = release.content_type
            data[rank]['content_encoding'] = release.content_encoding
        return data

    def file_versions(self, filepath):
        versions = []
        for release in self.get_releases(filepath):
            if release.key == None:
                versions.append((release.rank,None))
            else:
                versions.append((release.rank,release.version))
        return versions

    def copy_key(self, src_key_path, dst_key_path):
        """Copy src_key_path to dst_key_path """
        return self.bucket.copy_key(dst_key_path,self.bucket.name,src_key_path)

