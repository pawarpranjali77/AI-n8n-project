import json
from collections import deque

p = '/Users/pranjali/Downloads/workflow.json'
with open(p, 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes = wf.get('nodes', [])
connections = wf.get('connections', {})
node_names = {n['name'] for n in nodes}

# 1) every connection source key and every target node exists
for src, conns in connections.items():
    if src not in node_names:
        raise ValueError(f'Connection source key missing from nodes: {src}')
    for output_list in conns.values():
        for items in output_list:
            for item in items:
                target = item.get('node')
                if target not in node_names:
                    raise ValueError(f'Connection target missing from nodes: {target} (from {src})')

# 2) every non-trigger node is reachable from a trigger
trigger_names = {n['name'] for n in nodes if 'Trigger' in n['type']}
reachable = set()
queue = deque(trigger_names)
while queue:
    current = queue.popleft()
    if current in reachable:
        continue
    reachable.add(current)
    for src, conns in connections.items():
        if src != current:
            continue
        for output_list in conns.values():
            for items in output_list:
                for item in items:
                    target = item.get('node')
                    if target not in reachable:
                        queue.append(target)

non_trigger_nodes = {n['name'] for n in nodes if 'Trigger' not in n['type']}
missing = sorted(non_trigger_nodes - reachable)
if missing:
    raise ValueError(f'Non-trigger nodes are not reachable from a trigger: {missing}')

print('VALID: all connection keys/targets exist and all non-trigger nodes are reachable from a trigger.')
print('Node count:', len(nodes))
print('Trigger count:', len(trigger_names))
print('Reachable non-trigger count:', len(non_trigger_nodes & reachable))
