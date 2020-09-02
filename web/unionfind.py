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

class UnionFind:
    def __init__(self, length):
        self.length = length
        self.parents = [None for i in range(length)]
        self.block_weights = [1 for i in range(length)]
        self.custom_weights = [0 for i in range(length)]

    def merge(self, i, j):
        i = self.find(i)
        j = self.find(j)
        if i==j:
            return
        if self.block_weights[i] < self.block_weights[j]:
            i, j = j, i
        self.parents[j] = i
        self.block_weights[i] += self.block_weights[j]
        self.custom_weights[i] += self.custom_weights[j]

    def find(self, i):
        j = i
        while self.parents[j] is not None:
            j = self.parents[j]
        while i != j:
            k = self.parents[i]
            self.parents[i] = j
            i = k
        return j

    def positive_weight_groups(self):
        return [(i, self.custom_weights[i])
                for i in range(self.length)
                if self.parents[i] is None
                and self.custom_weights[i] > 0]
