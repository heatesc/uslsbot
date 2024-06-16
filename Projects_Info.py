import discord

class Projects_Info:
    def __init__(self, client, channel_id: int, message_id: int):
        self.client = client
        self.channel_id = channel_id
        self.message_id = message_id

    async def get_message(self):
        channel = self.client.get_channel(self.channel_id)
        if channel is None:
            raise ValueError(f"Channel with ID {self.channel_id} not found")
        try:
            message = await channel.fetch_message(self.message_id)
            return message
        except discord.NotFound:
            raise ValueError(f"Message with ID {self.message_id} not found in channel {self.channel_id}")
        except discord.Forbidden:
            raise ValueError(f"Bot does not have permission to access message with ID {self.message_id} in channel {self.channel_id}")

    async def update_message(self, new_content):
        message = await self.get_message()
        await message.edit(content=new_content)

    async def verify_message_editable(self):
        try:
            message = await self.get_message()
            await message.edit(content=message.content)
            return True
        except (discord.NotFound, discord.Forbidden, ValueError):
            return False

    def parse_message_content(self, content):
        projects = {}
        current_proj = None

        for line in content.split('\n'):
            if line.startswith('## '):
                current_proj = line[3:].strip()
                projects[current_proj] = {'Description': '', 'Admin': '', 'Contributors': []}
            elif line.strip().startswith('Description:'):
                projects[current_proj]['Description'] = line.split('Description: ', 1)[1].strip()
            elif line.strip().startswith('Project Admin:'):
                projects[current_proj]['Admin'] = line.split('Project Admin: <@', 1)[1][:-1].strip()
            elif line.strip().startswith('👉 <@'):
                projects[current_proj]['Contributors'].append(line.split('👉 <@', 1)[1][:-1].strip())

        return projects

    def format_message_content(self, projects):
        lines = ['# **Projects Info**']
        for proj, details in projects.items():
            lines.append(f'## {proj}')
            lines.append(f'  Description: {details["Description"]}')
            lines.append(f'  Project Admin: <@{details["Admin"]}>')
            lines.append('  Project contributors:')
            for contributor in details['Contributors']:
                lines.append(f'    👉 <@{contributor}>')

        return '\n'.join(lines)

    async def update_proj_desc(self, proj, new_desc):
        message = await self.get_message()
        projects = self.parse_message_content(message.content)

        if proj in projects:
            projects[proj]['Description'] = new_desc
        else:
            projects[proj] = {'Description': new_desc, 'Admin': '', 'Contributors': []}

        new_content = self.format_message_content(projects)
        await self.update_message(new_content)
    
    async def update_proj_name(self, proj, new_name) -> bool:
        message = await self.get_message()
        projects = self.parse_message_content(message.content)
        if not self.project_exists(proj):
            return False
        projects[new_name] = projects.pop(proj)
        new_content = self.format_message_content(projects)
        await self.update_message(new_content)
        return True

    async def update_proj_admin(self, proj, new_admin_id):
        message = await self.get_message()
        projects = self.parse_message_content(message.content)

        if proj in projects:
            projects[proj]['Admin'] = new_admin_id
            if new_admin_id not in projects[proj]['Contributors']:
                projects[proj]['Contributors'].append(new_admin_id)
        else:
            projects[proj] = {'Description': '', 'Admin': new_admin_id, 'Contributors': [new_admin_id]}

        new_content = self.format_message_content(projects)
        await self.update_message(new_content)

    async def add_proj_contributor(self, proj, contributor_id):
        message = await self.get_message()
        projects = self.parse_message_content(message.content)

        if proj in projects:
            if str(contributor_id) not in projects[proj]['Contributors']:
                projects[proj]['Contributors'].append(contributor_id)
            else:
                return False  # Contributor already exists
        else:
            projects[proj] = {'Description': '', 'Admin': '', 'Contributors': [contributor_id]}

        new_content = self.format_message_content(projects)
        await self.update_message(new_content)
        return True

    async def remove_proj_contributor(self, proj, contributor_id):
        message = await self.get_message()
        projects = self.parse_message_content(message.content)
        
        # debug
        print(projects)
        print(contributor_id)
        
        if proj in projects and str(contributor_id) in projects[proj]['Contributors']:
            projects[proj]['Contributors'].remove(str(contributor_id))
        else:
            return False  # Contributor does not exist

        new_content = self.format_message_content(projects)
        await self.update_message(new_content)
        return True

    async def get_proj_desc(self, proj):
        message = await self.get_message()
        projects = self.parse_message_content(message.content)
        return projects.get(proj, {}).get('Description', None)

    async def get_proj_admin(self, proj) -> int:
        message = await self.get_message()
        projects = self.parse_message_content(message.content)
        return int(projects.get(proj, {}).get('Admin', None))
    
    async def project_exists(self, proj):
        message = await self.get_message()
        projects = self.parse_message_content(message.content)
        return proj in projects

    async def remove_project(self, proj):
        message = await self.get_message()
        projects = self.parse_message_content(message.content)

        if proj in projects:
            del projects[proj]

        new_content = self.format_message_content(projects)
        await self.update_message(new_content)
