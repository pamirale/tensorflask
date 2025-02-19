# app.py
#
# A simple example of hosting a TensorFlow model as a Flask service
#
# Copyright 2017 ActiveState Software Inc.
# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import random
import time
import json
import os.path

from flask import Flask, jsonify, request

import numpy as np
import tensorflow as tf
import urllib3

app = Flask(__name__)

def load_graph(model_file):
  graph = tf.Graph()
  graph_def = tf.GraphDef()

  with tf.gfile.GFile(model_file, "rb") as f:
    graph_def.ParseFromString(f.read())
  with graph.as_default():
    tf.import_graph_def(graph_def)

  return graph

def read_tensor_from_image_file(file_name, input_height=299, input_width=299,
				input_mean=0, input_std=255):
  input_name = "file_reader"
  output_name = "normalized"
  file_reader = tf.read_file(file_name, input_name)
  image_reader = tf.image.decode_image(file_reader, channels = 3,
      name='image_reader')
  float_caster = tf.cast(image_reader, tf.float32)
  dims_expander = tf.expand_dims(float_caster, 0)
  resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
  normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
  sess = tf.Session()
  result = sess.run(normalized)

  return result

def load_labels(label_file):
  label = []
  proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
  for l in proto_as_ascii_lines:
    label.append(l.rstrip())
  return label

@app.route('/')
def classify():
    src_url = request.args['file']

    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs='/etc/ssl/certs/ca-certificates.crt')
    
    r = http.request('GET', src_url, preload_content=False)
    file_name = 'temp.jpg'
    with open(file_name, 'wb') as out:
        while True:
            data = r.read(65536)
            if not data:
                break
            out.write(data)
    
    r.release_conn()

    t = read_tensor_from_image_file(file_name,
                                  input_height=input_height,
                                  input_width=input_width,
                                  input_mean=input_mean,
                                  input_std=input_std)
        
    with tf.Session(graph=graph) as sess:
        start = time.time()
        results = sess.run(output_operation.outputs[0],
                      {input_operation.outputs[0]: t})
        end=time.time()
        results = np.squeeze(results)

        top_k = results.argsort()[-5:][::-1]
        labels = load_labels(label_file)

    print('\nEvaluation time (1-image): {:.3f}s\n'.format(end-start))
    
    # Build HTML output
    html = '<h2>Tensorflask results:</h2>' 
    for i in top_k:
      print(labels[i], results[i]) # Output to console
      html += '<p><b>{}</b> {:.4f}</p>'.format(labels[i], results[i])

    # Write file output
    output_file = '{}-output.txt'.format(os.path.splitext(file_name)[0])
    print('Output results file: {}'.format(output_file))
    with open(output_file, 'w') as f:
      json.dump([labels,results.tolist()], f, indent=1)

    return html

if __name__ == '__main__':
    # TensorFlow configuration/initialization
    model_file = "retrained_graph.pb"
    label_file = "retrained_labels.txt"
    input_height = 224
    input_width = 224
    input_mean = 128
    input_std = 128
    input_layer = "input"
    output_layer = "final_result"

    # Load TensorFlow Graph from disk
    graph = load_graph(model_file)

    # Grab the Input/Output operations
    input_name = "import/" + input_layer
    output_name = "import/" + output_layer
    input_operation = graph.get_operation_by_name(input_name)
    output_operation = graph.get_operation_by_name(output_name)

    # Initialize the Flask Service
    # Obviously, disable Debug in actual Production
    app.run(debug=True, port=8000)

