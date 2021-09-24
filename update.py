#!/usr/bin/env python3

import json
import os
import subprocess

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
APPS_DIR = os.path.join(ROOT_DIR, 'apps')


def create_app(base, app):
    ''' 
    Creates the ondemand app folder. 
    If the app folder already exists, it will not overwrite it.
    '''
    dest = os.path.join(APPS_DIR, app['app_name'])
    if os.path.exists(dest):
        return False

    os.makedirs(dest)
    copy_base_repo(base, app)
    update_form_and_manifest(base, app)
    return True


def copy_base_repo(base, app):
    '''
    Copies the base ondemand app from a github repository.
    '''
    base_dir = os.path.join(ROOT_DIR, base['git_dir'])
    if not os.path.exists(base_dir):
        exec_shell(f"git clone --single-branch --branch {base['git_branch']} {base['git_url']} {base_dir}")

    app_dir = os.path.join(APPS_DIR, app['app_name'])
    for filename in ('form.yml.erb', 'manifest.yml.erb', 'submit.yml.erb',  'template'):
        exec_shell(f"cp -R {base_dir}/{filename} {app_dir}/{filename}")


def update_form_and_manifest(base, app):
    '''
    Updates the form.yml and manifest.yml for the app.

    The assumption is that the base app has templates for these two files
    (i.e. form.yml.erb and manifest.yml.erb), and that we can update them 
    by applying ERB variables.
    
    Note that the "erb" CLI utility is part of the Ruby standard library,
    so you should have this if you have Ruby installed.
    '''
    app_type = base['app_type']
    app_dir = os.path.join(APPS_DIR, app['app_name'])
    # title for form.yml
    title = app['title']
    # name for manifest.yml
    name = app['name']
    
    use_custom_image_file = app.get('use_custom_image_file', base['use_custom_image_file'])

    vm_image = app.get('vm_image', base['vm_image'])
    base_image_select = vm_image.get('select', False)
    base_image = vm_image.get('base_image')

    memory = app.get("memory", {})
    memory_value = memory['value'] # required
    memory_select = memory.get('select', False)
    memory_min = memory.get('min')
    memory_max = memory.get('max')
    
    cpu = app.get("cpu", {})
    cpu_value = cpu['value'] # required
    cpu_select = cpu.get('select', False)
    cpu_min = cpu.get('min')
    cpu_max = cpu.get('max')

    # Prepare eRuby template vars 
    erb_vars = []
    erb_vars.append(f"@title = '{title}'")
    erb_vars.append(f"@name = '{name}'")
    if memory_select:
        erb_vars.append(f"@custom_memory_per_node_select = true")
        erb_vars.append(f"@custom_memory_per_node_min = {memory_min}")
        erb_vars.append(f"@custom_memory_per_node_max = {memory_max}")
    erb_vars.append(f"@custom_memory_per_node = {memory_value}")
    if cpu_select:
        erb_vars.append(f"@custom_num_cores_select = true")
        erb_vars.append(f"@custom_num_cores_min = {cpu_min}")
        erb_vars.append(f"@custom_num_cores_max = {cpu_max}")
    erb_vars.append(f"@custom_num_cores = {cpu_value}")
    if not base_image_select:
        erb_vars.append(f"@base_image_select = false")
        erb_vars.append(f"@base_image = {base_image}")
    else:
        erb_vars.append(f"@base_image_select = true")
    erb_vars.append(f"@use_custom_image_file = {str(use_custom_image_file).lower()}")

    erb_vars_file = os.path.join(app_dir, 'vars.rb')
    with open(erb_vars_file, "w") as f:
        f.write("\n".join(erb_vars) + "\n")

    # Apply template vars 
    exec_shell(f"erb -T - -r {erb_vars_file} {app_dir}/form.yml.erb > {app_dir}/form.yml")
    exec_shell(f"erb -T - -r {erb_vars_file} {app_dir}/manifest.yml.erb > {app_dir}/manifest.yml")
    
    # Cleanup
    exec_shell(f"rm {app_dir}/form.yml.erb")
    exec_shell(f"rm {app_dir}/manifest.yml.erb")
    exec_shell(f"rm {erb_vars_file}")


def exec_shell(cmd):
    ''' Execute a shell command. '''
    subprocess.check_call(cmd, shell=True)


def load_apps():
    ''' Loads JSON file that defines the app configurations. '''
    data = None
    with open(os.path.join(ROOT_DIR, 'apps.json'), 'r') as f:
        data = json.load(f)
    
    # quick sanity check
    for key in ('app_type', 'git_url', 'git_dir', 'git_branch', 'vm_image', 'use_custom_image_file'):
        assert key in data['base'], f"Base missing required attribute: {key}"
    for i, app in enumerate(data['apps']):
        for key in ('app_name', 'title', 'name', 'cpu', 'memory'):
            assert key in app, f"App {i} is missing required attribute: {key} {app}"

    return data


def main():
    data = load_apps()
    for app in data['apps']:
        created = create_app(data['base'], app)
        if created:
            print(f"Created {app['app_name']}")
        else:
            print(f"Skipped {app['app_name']} -- already created")


if __name__ == "__main__":
    main()
