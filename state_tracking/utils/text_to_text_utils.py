# Copyright 2021 Google Research.
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

"""Utils for creating text-to-text data."""

import dataclasses
import os
import random
from typing import Dict, MutableSequence

from lingvo import compat as tf


@dataclasses.dataclass
class TextToTextExample:
  """A single text-to-text dialogue example.

  Attributes:
    src: Input text for the model.
    tgt: Target text for the model.
    dialog_id: Id of dialog this example was generated from.
    turn: Turn of dialog this example was generated from.
    frame: Frame of the dialog this example was generated from.
  """
  src: str
  tgt: str
  dialog_id: str
  turn: int
  frame: int = 0


def write_data(examples: MutableSequence[TextToTextExample],
               output_path: str,
               shuffle: bool = True) -> None:
  """Writes examples to the given output path.

  Args:
    examples: A list of formatted examples to write out
    output_path: The file path to write examples out to
    shuffle: Whether to randomly shuffle examples
  """

  def _bytes_feature(value):
    """Returns a bytes_list from a string / byte."""
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

  def _int64_feature(value):
    """Returns an int64_list from a bool / enum / int / uint."""
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

  tf.io.gfile.makedirs(os.path.dirname(output_path))

  if shuffle:
    random.shuffle(examples)
  with tf.io.TFRecordWriter(output_path) as out_file:
    for example in examples:
      tf_example = tf.train.Example(
          features=tf.train.Features(
              feature={
                  'input':
                      _bytes_feature(example.src.encode('utf-8')),
                  'value':
                      _bytes_feature(example.tgt.encode('utf-8')),
                  'dialog_id':
                      _bytes_feature(example.dialog_id.encode('utf-8')),
                  'turn':
                      _int64_feature(example.turn)
              }))
      out_file.write(tf_example.SerializeToString())
    tf.logging.info('Wrote %s with %d examples', os.path.basename(output_path),
                    len(examples))


def decode_fn(record_bytes: tf.Tensor) -> Dict[str, tf.Tensor]:
  return tf.io.parse_single_example(
      record_bytes, {
          'input': tf.io.VarLenFeature(dtype=tf.string),
          'value': tf.io.VarLenFeature(dtype=tf.string),
          'dialog_id': tf.io.VarLenFeature(dtype=tf.string),
          'turn': tf.io.FixedLenFeature([], dtype=tf.int64)
      })
