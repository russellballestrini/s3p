from os import environ

from sys import (
  argv,
  exit
)

from boto.s3.connection import S3Connection

from boto.s3.key import Key

# valid ordered promotion ranks
ranks = ['operations', 'staging', 'production']

# required environment variables
required_environ = [
  'AWS_ACCESS_KEY_ID',
  'AWS_SECRET_ACCESS_KEY',
  'AWS_S3_BUCKET',
]

if all(var in environ for var in required_environ) == False:
    print('Required environment vars: ' + ', '.join(required_environ))
    exit(2)

# Constructor will fetch AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.
conn = S3Connection()
bucket = conn.get_bucket(environ['AWS_S3_BUCKET'])

def promote(bucket, filename, src, dst):
    """promote a file through the ranks"""
    try:
        k = Key(bucket, '/'.join([src,filename]))
        k.copy(bucket, '/'.join([dst,filename]))
    except:
        # this could happen if you try to skip rank ...
        return False

if __name__ == '__main__':
    try:
        filepath=argv[1]
        new_rank=argv[2]
        filename=filepath.split('/')[-1]
    except IndexError:
        print('Usage: python {} filepath new_rank'.format(argv[0]))
        exit(2)

    if new_rank not in ranks:
        print('error="invalid rank"')
        exit(2)

    new_rank_index = ranks.index(new_rank) 
    if new_rank_index == 0:
        k = Key(bucket,'/'.join([new_rank,filename]))
        k.set_contents_from_filename(filepath)
    else:
       if promote(bucket, filename, ranks[new_rank_index-1], ranks[new_rank_index]) == False:
           print('error="could not promote, trying to skip rank?"')
           exit(2)

    print('success="promoted {} to {}"'.format(filename,new_rank))
