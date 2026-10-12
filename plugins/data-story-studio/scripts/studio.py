#!/usr/bin/env python3
"""Read-only diagnostics and safe workspace initialization. No installation/config mutations."""
import argparse,json,os,pathlib,platform,shutil,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parent.parent

def doctor():
    checks={'python':{'ok':sys.version_info>=(3,10),'version':platform.python_version()}}
    for tool in ('node','npm','ffmpeg','ffprobe'):
        path=shutil.which(tool)
        checks[tool]={'ok':bool(path),'path':path}
        if path:
            result=subprocess.run([path,'-version' if tool.startswith('ff') else '--version'],capture_output=True,text=True,timeout=15)
            checks[tool]['version']=(result.stdout or result.stderr).splitlines()[0]
    checks['dashboard_ready']={'ok':checks['python']['ok']}
    checks['motion_system_ready']={'ok':all(checks[k]['ok'] for k in ('node','ffmpeg','ffprobe')),'note':'Also run node cli.js doctor in the copied motion runtime; canvas must resolve. No dependencies are installed by doctor.'}
    print(json.dumps(checks,ensure_ascii=False,indent=2))
    return 0 if checks['python']['ok'] else 1

def initialize(raw):
    target=pathlib.Path(raw).expanduser()
    if not target.is_absolute(): raise ValueError('--workspace must be an absolute path')
    # Inspect lexical ancestors before resolve so symlink indirection cannot hide a target.
    if '..' in target.parts: raise ValueError('Parent traversal is not allowed')
    if any(p.is_symlink() for p in [target,*target.parents]): raise ValueError('Symlink workspace paths are not allowed')
    target=target.resolve()
    if target==ROOT or ROOT in target.parents: raise ValueError('Workspace must be outside the plugin package')
    if target.exists(): raise ValueError('Choose a new workspace directory; existing directories are never overwritten')
    if not target.parent.is_dir(): raise ValueError('Workspace parent must already exist')
    # No execution or dependency download: copy only audited package source files.
    target.mkdir(mode=0o700)
    try:
        shutil.copytree(ROOT/'runtime',target/'.data-story-runtime',ignore=shutil.ignore_patterns('node_modules','__pycache__','*.pyc'))
        shutil.copytree(ROOT/'fixtures',target/'examples')
        (target/'data-story-workspace.json').write_text(json.dumps({'schema_version':1,'plugin':'data-story-studio','version':'0.1.0','runtime':'.data-story-runtime'},indent=2)+'\n')
    except Exception:
        # Preserve partial workspace for inspection; do not recursively delete user files.
        raise
    print(json.dumps({'workspace':str(target),'runtime':str(target/'.data-story-runtime'),'status':'initialized','next':'Read the plugin README. Dashboard needs Python only; motion also needs Node, canvas and FFmpeg.'},indent=2))
    return 0

def main():
    parser=argparse.ArgumentParser(description=__doc__); sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('doctor'); init=sub.add_parser('init');init.add_argument('--workspace',required=True)
    args=parser.parse_args()
    try: return doctor() if args.command=='doctor' else initialize(args.workspace)
    except (ValueError,OSError,subprocess.SubprocessError) as exc:
        print(json.dumps({'error':str(exc)}),file=sys.stderr);return 2
if __name__=='__main__':sys.exit(main())
