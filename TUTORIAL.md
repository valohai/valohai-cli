# valohai-cli Tutorial

Getting Started
---------------

If you don't already have an account, [create one][app].

First, log in using the client using `vh login`.  Your credentials will be used to
acquire an authentication token.  For your convenience, authentication tokens do not
expire, but you can audit your authentication tokens in the [app][app] at any time.

Linking a project
-----------------

If you imported our [example project](https://github.com/valohai/tensorflow-example) over
at the app, you should now clone it to a working copy of your own.

```bash
git clone https://github.com/valohai/tensorflow-example
cd tensorflow-example
```

Now that you are in the working directory, you can link it with a Valohai project.

Invoke `vh project link` and enter the number (likely 1) of the project you'd like to link.

Creating an execution
---------------------

In a linked project directory, you can use `vh execution run` to start a run in the cloud.

For instance, using the Tensorflow example, `vh execution run train` will run the "Train model" step.
You can use `vh execution run train --help` (or `vh ex r train --help`; commands may be abbreviated to
unique prefixes) to see all of the available arguments. All parameters and inputs declared in the step's
configuration are available as command-line arguments.

By default, in the interest of reproduceability, executions are created from the newest commit
published in the repository the project is linked to.  You can also create ad-hoc executions that upload
the contents of the project directory (sans any files ignored by `.gitignore` files) to the cloud before
creating an execution with the `--adhoc` flag; i.e. `vh ex r --adhoc train`.

To see the execution's progress in real time, you can add the `--watch` argument.
This is equivalent to invoking `vh ex watch N`, where N is the number of the execution.

Running a pipeline
------------------
In a linked project directory, you can start a pipeline run using `vh pipeline run <pipeline-name>`. 

Further steps
-------------

See `vh --help`. Each subcommand also has documentation of its own, also available via `--help`.

If you have any questions, please don't hesitate to contact us either via Github issues or the in-[app][app]
support system!


[vh]: https://valohai.com/
[app]: https://app.valohai.com/
