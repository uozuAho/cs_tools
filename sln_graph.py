#!python

from glob import glob
import json
import xml.etree.ElementTree as et

def find_opt_csprojs(root):
  """ find all csproj files under the current dir """
  return glob(f'{root}/**/*.csproj')

def get_all_project_refs(csproj_path):
  """ return all csproj files referenced by the given csproj """
  proj = et.parse(csproj_path)
  for ref in proj.iter('{http://schemas.microsoft.com/developer/msbuild/2003}ProjectReference'):
    yield ref.attrib['Include']

def build_csproj_adj_list(root):
  # returns dict of proj filename -- references --> [proj filename]
  # NOTE: no paths - just filenames
  adj = {}
  for proj_path in find_opt_csprojs(root):
    proj_filename = proj_path.split('\\')[-1]
    if proj_filename in adj:
      raise Exception(proj_filename + ' already in adj list!')
    adj[proj_filename] = list(p.split('\\')[-1] for p in get_all_project_refs(proj_path))
  return adj

def assert_all_refs_in_adj_list(adj_list):
  """ Throw an exception if any project references an unknown project """
  for proj in adj_list:
    for adj in adj_list[proj]:
      if adj not in adj_list:
        raise Exception('{} references {}, which was not found'.format((proj, adj)))

def build_json_graph(adj_list):
  jobj = { 'nodes': [{'id': p, 'label': p} for p in adj_list], 'edges': [] }
  for p in adj_list:
    jobj['edges'].extend([{'from': p, 'to': adj} for adj in adj_list[p]])
  return jobj


if __name__ == '__main__':
  import sys
  root = sys.argv[1] if len(sys.argv) == 2 else '.'
  adj = build_csproj_adj_list(root)
  assert_all_refs_in_adj_list(adj)
  jobj = build_json_graph(adj)
  print(json.dumps(jobj))
