#!/usr/bin/python

import datetime
import json
import numpy as np
from sys import argv

filename = argv[1]

filename_base = filename.split('.')[0]

with open(filename, 'r') as f:
    board = json.load(f)
    trueboard = np.array(board['tokens'])
    edges = board['edges']

base_line = '<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="black" stroke-width="0.5%">'
token_r = min(np.linalg.norm(trueboard[i]-trueboard[j])
    for (i, j) in edges) * 0.45
base_circle = '<circle cx="{}" cy="{}" r="{}" {}>'


with open(filename_base+'.svg','w') as f:
  f.write('<svg viewBox="0 0 44 44" xmlns="http://www.w3.org/2000/svg">')
  for (i,j) in edges:
    pt1 = trueboard[i]
    pt2 = trueboard[j]
    f.write(base_line.format(
        pt1[0]+22,
        pt1[1]+22,
        pt2[0]+22,
        pt2[1]+22
    ))

    f.write('</line>')
  for (i,pt) in enumerate(trueboard):
    num_adjacent = sum(
        (j==i or k==i) for (j,k) in edges
    )
    fill = 'fill-opacity="0"'
    if num_adjacent==5:
      fill = 'fill="red"'
    if num_adjacent==7:
      fill = 'fill="blue"'
    f.write(base_circle.format(
        pt[0]+22,
        pt[1]+22,
        token_r,
        fill
    ))
    f.write('<title>')
    f.write('cell {}'.format(i))
    f.write('</title>')
    f.write('</circle>')
  f.write('</svg>')