#!python

from argparse import ArgumentParser

from s3p import S3Pipeline

def build_base_subparser(parser, optional_rank=False):
    parser.add_argument('filepath', help='filename or filepath')
    rank_help='position in pipeline'
    if optional_rank:
        parser.add_argument('rank', nargs='?', default=None, help=rank_help)
    else:
        parser.add_argument('rank', help=rank_help)
    return parser

def build_promote_subparser(parser):
    parser = build_base_subparser(parser)
    parser.add_argument('version', nargs='?', default=None,
        help='version identifier, timestamp, md5, commit hash, etc')
    parser.set_defaults(func=promote)

def build_version_subparser(parser):
    parser = build_base_subparser(parser, optional_rank=True)
    parser.set_defaults(func=version)

def build_download_subparser(parser):
    parser = build_base_subparser(parser)
    parser.add_argument('download_path', nargs='?', default=None,
        help='location to download file to')
    parser.set_defaults(func=download)

def build_parser():
    parser = ArgumentParser(
        description="Build process and piplelines on AWS S3 for release promotion")
    subparsers = parser.add_subparsers(title='subcommands',
        description='valid subcommands', help='--help for additional subcommand help')
    build_promote_subparser(subparsers.add_parser('promote',
        description='Promote releases through pipeline ranks.'))
    build_version_subparser(subparsers.add_parser('version',
        description='Get release version info from one or all pipeline ranks.'))
    build_download_subparser(subparsers.add_parser('download',
        description='Download release from rank to local filesystem.'))
    return parser

def promote(args):
    pipeline = S3Pipeline()
    release = pipeline.get_release(args.filepath, args.rank)
    try:
        result = release.promote(args.version)
    except:
        return 'error="could not promote, trying to skip rank?"'

    if result == None:
        return 'success="promoted {} version {} to {} rank"'.format(
            release.filename, release.version, release.rank)
    else:
        return 'warning="{}"'.format(result)

def version(args):
    pipeline = S3Pipeline()
    if args.rank == None:
        output = []
        versions = pipeline.file_versions(args.filepath)
        for version in versions:
            output.append('{}="{}"'.format(*version))
        return '\n'.join(output)
    else:
        release = pipeline.get_release(args.filepath, args.rank)
        return '{}="{}"'.format(release.rank,release.version)

def download(args):
    pipeline = S3Pipeline()
    release = pipeline.get_release(args.filepath, args.rank)
    if args.download_path == None:
        args.download_path = release.rank+'-'+release.filename
    release.download(args.download_path)
    return 'success="downloaded {} version {} from rank {} to {}"'.format(
        release.filename,release.version,release.rank,args.download_path)

def main():
    parser = build_parser()
    args = parser.parse_args()
    print(args.func(args))
