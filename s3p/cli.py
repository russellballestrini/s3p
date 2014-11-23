#!python

from argparse import ArgumentParser

from s3p import S3Pipeline

def main():
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

    pipeline = S3Pipeline()

    if args.info == True:
        print(pipeline.file_info(args.filepath))
        exit()

    if args.get_versions == True:
        versions = pipeline.file_versions(args.filepath)
        for version in versions:
            print('{}="{}"'.format(*version))
        exit()

    #release = pipeline.get_release(args.filepath, args.rank)
    try:
        release = pipeline.get_release(args.filepath, args.rank)
    except:
        print('error="invalid rank"')
        exit(2)

    if args.get_version == True:
        print('{}="{}"'.format(release.rank,release.version))
        exit()

    if args.download_path != None:
        release.download(args.download_path)
        exit()

    result = release.promote(args.version)
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
