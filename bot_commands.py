import discord
from discord import app_commands
from Projects_Info import Projects_Info
import os

OWNER_USER_ID = int(os.getenv('OWNER_USER_ID'))

def add_cmd_see_projects(tree: app_commands.CommandTree):
    @tree.command(name='see_projects', description='Provides information about projects')
    async def see_projects(interaction: discord.Interaction):
        await interaction.response.send_message(f'{interaction.user.mention} see #projects-info')


def add_cmd_set_proj_desc(tree: app_commands.CommandTree, proj_info: Projects_Info):
    @tree.command(name='set_proj_desc', description='Set the project description')
    @app_commands.describe(proj='Project name', new_desc='New project description')
    async def set_proj_desc(interaction: discord.Interaction, proj: str, new_desc: str):
        await proj_info.update_proj_desc(proj, new_desc)
        await interaction.response.send_message(f'Updated project {proj} description to "{new_desc}"')


def add_cmd_get_proj_desc(tree: app_commands.CommandTree, proj_info: Projects_Info):
    @tree.command(name='get_proj_desc', description='Get the project description')
    @app_commands.describe(proj='Project name')
    async def get_proj_desc(interaction: discord.Interaction, proj: str):
        description = await proj_info.get_proj_desc(proj)
        if description:
            await interaction.response.send_message(f'Description for project {proj}: {description}')
        else:
            await interaction.response.send_message(f'No description found for project {proj}')


def add_cmd_create_project(tree: app_commands.CommandTree, proj_info: Projects_Info):
    @tree.command(name='create_project', description='Create a new project')
    @app_commands.describe(pname='Project name', padmin='Project admin')
    async def create_project(interaction: discord.Interaction, pname: str, padmin: discord.User):
        if interaction.user.id != OWNER_USER_ID:
            await interaction.response.send_message('Only the owner can create new projects.', ephemeral=True)
            return

        existing_description = await proj_info.get_proj_desc(pname)
        if existing_description:
            await interaction.response.send_message(f'Project {pname} already exists.', ephemeral=True)
        else:
            await proj_info.update_proj_desc(pname, '')
            await proj_info.update_proj_admin(pname, padmin.id)
            await interaction.response.send_message(f'Project {pname} created with admin {padmin.mention}.')


def add_cmd_project_add_member(tree: app_commands.CommandTree, proj_info: Projects_Info):
    @tree.command(name='project_add_member', description='Add a member to a project')
    @app_commands.describe(pname='Project name', new_member='New member')
    async def project_add_member(interaction: discord.Interaction, pname: str, new_member: discord.User):
        project_admin_id = await proj_info.get_proj_admin(pname)
        if interaction.user.id != OWNER_USER_ID and interaction.user.id != project_admin_id:
            await interaction.response.send_message('Only the owner or project admin can add members.', ephemeral=True)
            return

        success = await proj_info.add_proj_contributor(pname, new_member.id)
        if success:
            await interaction.response.send_message(f'Added {new_member.mention} to project {pname}.')
        else:
            await interaction.response.send_message(f'{new_member.mention} is already a member of project {pname}.', ephemeral=True)


def add_cmd_project_kick_member(tree: app_commands.CommandTree, proj_info: Projects_Info):
    @tree.command(name='project_kick_member', description='Kick a member from a project')
    @app_commands.describe(pname='Project name', member_name='Member name')
    async def project_kick_member(interaction: discord.Interaction, pname: str, member_name: discord.User):
        project_admin_id = await proj_info.get_proj_admin(pname)
        if interaction.user.id != OWNER_USER_ID and interaction.user.id != project_admin_id:
            await interaction.response.send_message('Only the owner or project admin can kick members.', ephemeral=True)
            return

        success = await proj_info.remove_proj_contributor(pname, member_name.id)
        if success:
            await interaction.response.send_message(f'Removed {member_name.mention} from project {pname}.')
        else:
            await interaction.response.send_message(f'{member_name.mention} is not a member of project {pname}.', ephemeral=True)


def add_cmd_remove_project(tree: app_commands.CommandTree, proj_info: Projects_Info):
    @tree.command(name='remove_project', description='Remove a project')
    @app_commands.describe(pname='Project name')
    async def remove_project(interaction: discord.Interaction, pname: str):
        project_admin_id = await proj_info.get_proj_admin(pname)
        if interaction.user.id != OWNER_USER_ID and interaction.user.id != project_admin_id:
            await interaction.response.send_message('Only the owner or project admin can remove projects.', ephemeral=True)
            return

        await proj_info.remove_project(pname)
        await interaction.response.send_message(f'Project {pname} has been removed.')

def add_cmd_change_proj_admin(tree: app_commands.CommandTree, proj_info: Projects_Info):
    @tree.command(name='change_proj_admin', description='Change the project admin')
    @app_commands.describe(proj='Project name', new_admin='New admin')
    async def change_proj_admin(interaction: discord.Interaction, proj: str, new_admin: discord.User):
        project_admin_id = await proj_info.get_proj_admin(proj)
        if interaction.user.id != OWNER_USER_ID and interaction.user.id != project_admin_id:
            await interaction.response.send_message('Only the owner or current project admin can change the admin.', ephemeral=True)
            return

        await proj_info.update_proj_admin(proj, new_admin.id)
        await interaction.response.send_message(f'Changed admin for project {proj} to {new_admin.mention}.')

def add_commands(tree: app_commands.CommandTree, proj_info: Projects_Info):
    add_cmd_see_projects(tree)
    add_cmd_set_proj_desc(tree, proj_info)
    add_cmd_get_proj_desc(tree, proj_info)
    add_cmd_create_project(tree, proj_info)
    add_cmd_project_add_member(tree, proj_info)
    add_cmd_project_kick_member(tree, proj_info)
    add_cmd_remove_project(tree, proj_info)
    add_cmd_change_proj_admin(tree, proj_info)
