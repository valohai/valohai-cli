import click

from valohai_cli.utils import match_prefix


def build_nodes(commit, config, pipeline):
    nodes = []
    for node in pipeline.nodes:
        step = config.steps.get(node.step)
        template = build_node_template(commit, step)
        nodes.append({
            "name": node.name,
            "type": node.type,
            "template": template,
        })
    return nodes


def build_node_template(commit, step):
    template = {
        "commit": commit,
        "step": step.name,
        "image": step.image,
        "command": step.command,
        "inputs": {
            key: step.inputs[key].default for key in list(step.inputs)
        },
        "parameters": {
            key: step.parameters[key].default for key in
            list(step.parameters)
        },
        "inherit_environment_variables": True,
        "environment_variables": {
            envvar.key(): envvar.value() for envvar in step.environment_variables
        }
    }
    if step.environment:
        template["environment"] = step.environment
    return template


def build_edges(pipeline):
    return list({
        "source_node": edge.source_node,
        "source_key": edge.source_key,
        "source_type": edge.source_type,
        "target_node": edge.target_node,
        "target_type": edge.target_type,
        "target_key": edge.target_key,
    } for edge in pipeline.edges)


def match_pipeline(config, pipeline_name):
    """
    Take a pipeline name and try and match it to the configs pipelines.
    Returns the match if there is only one option.
    """
    if pipeline_name in config.pipelines:
        return pipeline_name
    matching_pipelines = match_prefix(config.pipelines, pipeline_name, return_unique=False)
    if not matching_pipelines:
        raise click.BadParameter(
            '"{pipeline}" is not a known pipeline (try one of {pipelines})'.format(
                pipeline=pipeline_name,
                pipelines=', '.join(click.style(t, bold=True) for t in sorted(config.pipelines))
            ), param_hint='pipeline')
    if len(matching_pipelines) > 1:
        raise click.BadParameter(
            '"{pipeline}" is ambiguous.\nIt matches {matches}.\nKnown pipelines are {pipelines}.'.format(
                pipeline=pipeline_name,
                matches=', '.join(click.style(t, bold=True) for t in sorted(matching_pipelines)),
                pipelines=', '.join(click.style(t, bold=True) for t in sorted(config.pipelines)),
            ), param_hint='pipeline')
    return matching_pipelines[0]
