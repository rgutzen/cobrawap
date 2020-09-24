import os
import yaml
import warnings

def safe_open_w(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, 'w')


def read_stage_output(stage, config_dir, config_name, output_namespace="STAGE_OUTPUT"):
    with open(os.path.join(config_dir, stage, config_name), 'r') as f:
        config_dict = yaml.safe_load(f)
    if config_dict is None:
        warnings.warn(f'config file {os.path.join(config_dir, stage, config_name)} can not be loaded! Skipping reading stage output.')
        return None
    elif output_namespace in config_dict.keys():
        return config_dict[output_namespace]
    else:
        raise ValueError(f"config file of stage {stage} "
                       + f"does not define {output_namespace}!")


def create_temp_configs(stages, working_dir, config_name, output_dir, temp_name='temp_config.yaml'):
    for i, stage in enumerate(stages):
        config_path = os.path.join(working_dir, stage, config_name)
        new_config_path = os.path.join(output_dir, stage, temp_name)
        with open(config_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        with safe_open_w(new_config_path) as f:
            f.write(yaml.dump(config_dict, default_flow_style=False))
    return None

def update_configfile(config_path, update_dict):
    # Careful! This function overwrites the config file.
    # Comments in the file are lost.
    with open(config_path, 'r') as f:
        try:
            config_dict = yaml.safe_load(f)
        except Exception as e:
            print(e)
            config_dict = None
    if config_dict is None:
        warnings.warn(f'config file {config_path} can not be loaded! Skipping updating config.')
        return None
    config_dict.update(**update_dict)
    with safe_open_w(config_path) as f:
        f.write(yaml.dump(config_dict, default_flow_style=False))
    return None

def set_stage_inputs(stages, output_dir, config_file='temp_config.yaml',
                     intput_namespace="STAGE_INPUT"):
    update_dict = {}
    for i, stage in enumerate(stages[:-1]):
        output_name = read_stage_output(stage,
                                        config_dir=output_dir,
                                        config_name=config_file)
        if output_name is None:
            warnings.warn(f'Could not read stage output for {stage}! Skipping setting input for subsequent stage.')
        else:
            update_dict[intput_namespace] = os.path.join(output_dir, stage, output_name)
            update_configfile(config_path=os.path.join(output_dir, stages[i+1], config_file),
                              update_dict=update_dict)
    return None

def set_global_configs(stages, output_dir, config_dict, config_file='temp_config.yaml'):
    for stage in stages:
        update_configfile(config_path=os.path.join(output_dir, stage, config_file),
                          update_dict=config_dict)
    return None
