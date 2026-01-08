PYTHON_SOURCE_USING_VALOHAI_UTILS = """
import os

import valohai

params = {
    "param1": True,
    "param2": "asdf",
    "param3": 123,
    "param4": 0.0001,
}

inputs = {"input1": "asdf", "input2": ["yolol", "yalala"]}


def prepare(a, b):
    print("this is fake method %s %s" % (a, b))


valohai.prepare(step="foobar1", parameters=params, inputs=inputs)
"""
PYTHON_SOURCE = """
import os

print("I'm just a poor boy without any utils.")
"""
PYTHON_SOURCE_DEFINING_PIPELINE = """
from valohai import Pipeline


def main(config) -> Pipeline:
    pipe = Pipeline(name="mypipeline", config=config)

    # Define nodes
    extract = pipe.execution("Batch feature extraction")
    train = pipe.task("Train model")
    evaluate = pipe.execution("Evaluate")

    # Configure training task node
    train.linear_parameter("learning_rate", min=0, max=1, step=0.1)

    # Configure pipeline
    extract.output("a*").to(train.input("aaa"))
    extract.output("a*").to(train.input("bbb"))
    train.output("*").to(evaluate.input("models"))

    return pipe
"""
