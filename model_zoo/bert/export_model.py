# Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
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

import argparse
import os

import paddle
from run_glue_trainer import MODEL_CLASSES


def parse_args():
    parser = argparse.ArgumentParser()

    # Required parameters
    parser.add_argument(
        "--model_type",
        default=None,
        type=str,
        required=True,
        help="Model type selected in the list: " + ", ".join(MODEL_CLASSES.keys()),
    )
    parser.add_argument(
        "--model_path",
        default=None,
        type=str,
        required=True,
        help="Model name or path of the trained model to be exported.",
    )
    parser.add_argument(
        "--output_path",
        default=None,
        type=str,
        help="The output file prefix used to save the exported inference model.",
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    args.model_type = args.model_type.lower()
    if args.model_type == "bert":
        model_class, tokenizer_class = MODEL_CLASSES["bert"]
        print(
            r"""
 ____            _
| __ )  ___ _ __| |_
|  _ \ / _ \ '__| __|
| |_) |  __/ |  | |_
|____/ \___|_|   \__|

    {}""".format(
                "\n    ".join(model_class.pretrained_init_configuration.keys())
            )
        )
    elif args.model_type == "ernie":
        model_class, tokenizer_class = MODEL_CLASSES["ernie"]
        print(
            r"""
 _____            _
| ____|_ __ _ __ (_) ___
|  _| | '__| '_ \| |/ _ \
| |___| |  | | | | |  __/
|_____|_|  |_| |_|_|\___|

    {}""".format(
                "\n    ".join(model_class.pretrained_init_configuration.keys())
            )
        )
    else:
        raise ValueError(
            "model type only supports: {}, but your model type is {}".format(
                ",".join(MODEL_CLASSES), args.model_type
            )
        )

    if args.output_path is None:
        args.output_path = "{}{}inference".format(
            os.path.abspath(args.model_path), os.path.sep
        )
    
    # build model and load trained parameters
    model = model_class.from_pretrained(args.model_path)
    # switch to eval model
    model.eval()
    # convert to static graph with specific input description
    model = paddle.jit.to_static(
        model,
        input_spec=[
            paddle.static.InputSpec(shape=[None, None], dtype="int64"),  # input_ids
            paddle.static.InputSpec(shape=[None, None], dtype="int64"),  # segment_ids
        ],
    )
    # save converted static graph model
    paddle.jit.save(model, args.output_path)
    # also save tokenizer for inference usage
    tokenizer = tokenizer_class.from_pretrained(args.model_path)
    tokenizer.save_pretrained(os.path.dirname(args.output_path))


if __name__ == "__main__":
    main()
