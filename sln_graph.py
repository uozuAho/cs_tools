#!python

from glob import glob
import json
import xml.etree.ElementTree as et

def find_csprojs(root):
  """ find all csproj files under the current dir """
  return glob(f'{root}/*/**/*.csproj')

def get_all_project_refs(csproj_path):
  """ return all csproj files referenced by the given csproj """
  proj = et.parse(csproj_path)
  for ref in proj.iter('ProjectReference'):
    yield ref.attrib['Include']

def build_csproj_adj_list(projects):
  # returns dict {proj filename : [proj filename 1, proj filename 2]}
  # NOTE: no paths - just filenames
  adj = {}
  for proj_path in projects:
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

def to_json(adj_list):
  jobj = { 'nodes': [{'id': p, 'label': p} for p in adj_list], 'edges': [] }
  for p in adj_list:
    jobj['edges'].extend([{'from': p, 'to': adj} for adj in adj_list[p]])
  return json.dumps(jobj)

def to_networkx(adj_list):
  # pip install networkx
  import networkx as nx
  g = nx.Graph()
  g.add_nodes_from(adj_list.keys())
  for proj in adj_list:
    for dep in adj_list[proj]:
      g.add_edge(proj, dep)
  return g

def draw(adj_list):
  # pip install networkx
  # pip install matplotlib
  import networkx as nx
  import matplotlib.pyplot as plt
  nx.draw(to_networkx(adj_list))
  plt.show()

def to_graphviz_stdout(adj_list):
  # pip install networkx
  # pip install pydot
  import sys
  import networkx as nx
  from networkx.drawing.nx_pydot import write_dot
  return write_dot(to_networkx(adj_list), sys.stdout)

if __name__ == '__main__':
  import sys
  root = sys.argv[1] if len(sys.argv) == 2 else '.'
  cs_projects = find_csprojs(root)
  adj = build_csproj_adj_list(cs_projects)
  assert_all_refs_in_adj_list(adj)
  # print(to_json(adj))
  # draw(adj)
  # try https://dreampuf.github.io/GraphvizOnline or google graphviz online
  to_graphviz_stdout(adj)
