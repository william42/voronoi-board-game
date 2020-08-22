#!/usr/bin/python
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np
import scipy.spatial as sp
import math
import datetime
import json


def centroid(points):
    area = 0.0
    pta = np.array([0.0, 0.0])
    for i in range(len(points)):
        x = points[i-1]
        y = points[i]
        wt = x[0]*y[1]-y[0]*x[1]
        area += wt
        pta += (x+y) * wt
    return pta / (area * 3)


def cvcirc(pts, n, r):
    circ = np.array([[math.cos(2*math.pi*i/n), math.sin(2*math.pi*i/n)]
                     for i in range(n)])
    pts_aug = np.concatenate([pts, circ * r])
    vor = sp.Voronoi(pts_aug)
    return np.array(
        [centroid([vor.vertices[n] for n in region])
         for region in vor.regions
         if len(region) > 0 and -1 not in region])


def voroboard(n_i, n_b, ic):
    rng = np.random.default_rng()
    pts = rng.standard_normal([n_i, 2])
    for unused_i in range(ic):
        n_c = len(pts)
        pts = cvcirc(pts, n_b, 20)
        if len(pts) < n_c:
            print('small: ', len(pts))
            n_a = n_c - len(pts)
            pts = np.append(pts, rng.standard_normal([n_a, 2]), 0)
        if len(pts) > n_c:
            print('big: ', len(pts))
            pts = pts[:n_c]
        for j in range(n_c):
            if np.linalg.norm(pts[j]) > 19.75:
                pts[j] = rng.standard_normal([2]) * 4
    return pts


def circle(n):
    return np.array([[math.cos(2*math.pi*i/n), math.sin(2*math.pi*i/n)] for i in range(n)])


n = 51
board = voroboard(310, n, 800)
trueboard = np.concatenate([circle(n) * 20, board])
delb = sp.Delaunay(trueboard)

ptr, indices = delb.vertex_neighbor_vertices
edges = {(int(i), int(j)) for i in range(len(trueboard))
         for j in indices[ptr[i]:ptr[i+1]]
         if i < j}

now = datetime.datetime.now()
filename_base = 'board-alpha-{}-{}-{}-{}-{}-{}'.format(
    now.year,
    now.month,
    now.day,
    now.hour,
    now.minute,
    now.second
)
with open(filename_base+'.json', 'w') as f:
    res = {
        'tokens': trueboard.tolist(),
        'edges': list(edges),
    }
    json.dump(res, f)
