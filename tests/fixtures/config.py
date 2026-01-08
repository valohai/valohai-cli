CONFIG_YAML = """
---

- step:
    name: Train model
    image: busybox
    command: "false"
    inputs:
      - name: in1
        default: http://example.com/
    parameters:
      - name: max_steps
        pass-as: --max_steps={v}
        description: Number of steps to run the trainer
        type: integer
        default: 300
      - name: learning_rate
        type: float
        default: 0.1337
      - name: enable_mega_boost
        type: flag
      - name: multi-parameter
        default: ["one","two","three"]
        type: string
        multiple: separate
    environment-variables:
      - name: testenvvar
        default: 'test'
- endpoint:
    name: greet
    image: python:3.9
    port: 8000
    server-command: python -m wsgiref.simple_server
- endpoint:
    name: predict-digit
    description: predict digits from image inputs ("file" parameter)
    image: tensorflow/tensorflow:2.6.0
    wsgi: predict:predict
    files:
      - name: model
        description: Model output file from TensorFlow
        path: model.h5
"""
PIPELINE_YAML = (
    CONFIG_YAML
    + """
- step:
    name: Preprocess dataset (MNIST)
    image: tensorflow/tensorflow:1.13.1-gpu-py3
    command: python preprocess.py
    parameters:
      - name: sources
        type: string
        multiple: separate
        multiple-separator: '-'
        default:
        - port
        - railyard
    inputs:
      - name: training-set-images
        default: https://valohaidemo.blob.core.windows.net/mnist/train-images-idx3-ubyte.gz
      - name: training-set-labels
        default: https://valohaidemo.blob.core.windows.net/mnist/train-labels-idx1-ubyte.gz
      - name: test-set-images
        default: https://valohaidemo.blob.core.windows.net/mnist/t10k-images-idx3-ubyte.gz
      - name: test-set-labels
        default: https://valohaidemo.blob.core.windows.net/mnist/t10k-labels-idx1-ubyte.gz

- step:
    name: Train model (MNIST)
    image: tensorflow/tensorflow:1.13.1-gpu-py3
    command: python train.py {parameters}
    parameters:
      - name: max_steps
        pass-as: --max_steps={v}
        description: Number of steps to run the trainer
        type: integer
        default: 300
      - name: learning_rate
        pass-as: --learning_rate={v}
        description: Initial learning rate
        type: float
        default: 0.001
      - name: dropout
        pass-as: --dropout={v}
        description: Keep probability for training dropout
        type: float
        default: 0.9
      - name: batch_size
        pass-as: --batch_size={v}
        description: Training batch size (larger batches are usually more efficient on GPUs)
        type: integer
        default: 200
    inputs:
      - name: training-set-images
        default: https://valohaidemo.blob.core.windows.net/mnist/train-images-idx3-ubyte.gz
      - name: training-set-labels
        default: https://valohaidemo.blob.core.windows.net/mnist/train-labels-idx1-ubyte.gz
      - name: test-set-images
        default: https://valohaidemo.blob.core.windows.net/mnist/t10k-images-idx3-ubyte.gz
      - name: test-set-labels
        default: https://valohaidemo.blob.core.windows.net/mnist/t10k-labels-idx1-ubyte.gz

- step:
    name: Batch inference (MNIST)
    image: tensorflow/tensorflow:1.13.1-py3
    command:
      - pip install --disable-pip-version-check --quiet -r requirements.txt
      - python batch_inference.py --model-dir=/valohai/inputs/model/ --image-dir=/valohai/inputs/images
    inputs:
      - name: model
      - name: images
        default:
          - https://valohaidemo.blob.core.windows.net/mnist/four-inverted.png
          - https://valohaidemo.blob.core.windows.net/mnist/five-inverted.png
          - https://valohaidemo.blob.core.windows.net/mnist/five-normal.jpg

- step:
    name: Compare predictions (MNIST)
    image: tensorflow/tensorflow:1.13.1-py3
    command: python compare.py --prediction-dir=/valohai/inputs/predictions/
    inputs:
      - name: predictions

- step:
    name: Worker environment check
    image: tensorflow/tensorflow:1.13.1-gpu-py3
    command:
      - pwd
      - ls -la
      - nvidia-smi
      - python --version
      - nvcc --version | grep release

- pipeline:
    name: Training Pipeline
    nodes:
      - name: preprocess
        type: execution
        step: Preprocess dataset (MNIST)
      - name: train
        type: execution
        step: Train model (MNIST)
        override:
          inputs:
            - name: training-set-images
            - name: training-set-labels
            - name: test-set-images
            - name: test-set-labels
      - name: evaluate
        type: execution
        step: Batch inference (MNIST)
    edges:
      - [preprocess.output.*train-images*, train.input.training-set-images]
      - [preprocess.output.*train-labels*, train.input.training-set-labels]
      - [preprocess.output.*test-images*, train.input.test-set-images]
      - [preprocess.output.*test-labels*, train.input.test-set-labels]
      - [train.output.model*, evaluate.input.model]
    parameters:
      - name: pipeline_max_steps
        default: 1000
        targets:
            - Train model (MNIST).parameters.max_steps

- pipeline:
    name: Train Pipeline
    nodes:
      - name: preprocess
        type: execution
        step: Preprocess dataset (MNIST)
      - name: train
        type: execution
        step: Train model (MNIST)
        override:
          inputs:
            - name: training-set-images
            - name: training-set-labels
            - name: test-set-images
            - name: test-set-labels
      - name: evaluate
        type: execution
        step: Batch inference (MNIST)
    edges:
      - [preprocess.output.*train-images*, train.input.training-set-images]
      - [preprocess.output.*train-labels*, train.input.training-set-labels]
      - [preprocess.output.*test-images*, train.input.test-set-images]
      - [preprocess.output.*test-labels*, train.input.test-set-labels]
      - [train.output.model*, evaluate.input.model]
    parameters:
      - name: pipeline_max_steps
        default: 1000
        targets:
            - Train model (MNIST).parameters.max_steps
      - name: sources
        default: [airport]
        targets:
            - preprocess.parameters.sources
"""
)
YAML_WITH_EXTRACT_TRAIN_EVAL = """
- step:
    name: Batch feature extraction
    image: ubuntu:18.04
    command:
      - date > /valohai/outputs/aaa.md5
      - date > /valohai/outputs/bbb.sha256
- step:
    name: Train model
    image: ubuntu:18.04
    command:
      - find /valohai/inputs -type f -exec sha1sum '{}' ';' > /valohai/outputs/model.txt
    parameters:
      - name: learning_rate
        pass-as: --learning_rate={v}
        description: Initial learning rate
        type: float
        default: 0.001
    inputs:
      - name: aaa
      - name: bbb
- step:
    name: Evaluate
    image: ubuntu:18.04
    inputs:
      - name: models
    command:
      - ls -lar
"""
YAML_WITH_TRAIN_EVAL = """
- step:
    name: Train model
    image: ubuntu:18.04
    command:
      - find /valohai/inputs -type f -exec sha1sum '{}' ';' > /valohai/outputs/model.txt
    parameters:
      - name: learning_rate
        pass-as: --learning_rate={v}
        description: Initial learning rate
        type: float
        default: 0.001
    inputs:
      - name: aaa
      - name: bbb
- step:
    name: Evaluate
    image: ubuntu:18.04
    inputs:
      - name: models
    command:
      - ls -lar
"""
INVALID_CONFIG_YAML = """
---

- step:
    image: 8
    command:
      foo: 6
      bar: n
    outputs: yes
    parameters:
      - name: a
        type: integer
      - 38

"""
BROKEN_CONFIG_YAML = """'"""
KUBE_RESOURCE_YAML = """
---

- step:
    name: Train model
    image: busybox
    command: "false"
    inputs:
      - name: in1
        default: http://example.com/
    parameters:
      - name: max_steps
        pass-as: --max_steps={v}
        description: Number of steps to run the trainer
        type: integer
        default: 300
      - name: learning_rate
        type: float
        default: 0.1337
      - name: enable_mega_boost
        type: flag
      - name: multi-parameter
        default: ["one","two","three"]
        type: string
        multiple: separate
    environment-variables:
      - name: testenvvar
        default: 'test'
    resources:
      cpu:
        min: 1.0
        max: 2
      memory:
        min: 3
        max: 4
      devices:
        nvidia.com/gpu: 1
- endpoint:
    name: greet
    image: python:3.9
    port: 8000
    server-command: python -m wsgiref.simple_server
- endpoint:
    name: predict-digit
    description: predict digits from image inputs ("file" parameter)
    image: tensorflow/tensorflow:2.6.0
    wsgi: predict:predict
    files:
      - name: model
        description: Model output file from TensorFlow
        path: model.h5
"""
CACHE_VOLUME_YAML = """
---

- step:
    name: Train model
    image: busybox
    command: "false"
    cache-volumes:
      - default-cache-pvc
      - another-cache-pvc
"""
PIPELINE_WITH_TASK_EXAMPLE = """
- step:
    name: preprocess
    image: python:3.7
    command:
      - python ./preprocess.py
- step:
    name: train
    image: python:3.7
    command:
      - pip install valohai-utils
      - python ./train.py {parameters}
    parameters:
      - name: id
        type: string
- pipeline:
    name: dynamic-task
    nodes:
      - name: preprocess
        step: preprocess
        type: execution
      - name: train-with-errors
        step: train
        type: task
        on-error: "continue"
      - name: train-optional
        step: train
        type: task
        on-error: "stop-next"
      - name: train-critical
        step: train
        type: task
        on-error: "stop-all"
    edges:
      - [preprocess.metadata.storeids, train-critical.parameter.id]
      - [preprocess.metadata.storeids, train-optional.parameter.id]
      - [preprocess.metadata.storeids, train-with-errors.parameter.id]
"""
