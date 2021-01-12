import discord
import re
from   discord.ext import commands
from _Utils import Nullify

client = None

def setup(client):
    client.add_cog(DisplayName(client))

class DisplayName(commands.Cog):
    def __init__(self,client):
        self.client = client

    def clean_message(self, message, *, client = None, server = None, nullify = True):
        
        if nullify:
            zerospace = "​"
            message = message.replace("@everyone", "@{}everyone".format(zerospace)).replace("@here", "@{}here".format(zerospace))
        matches_re = re.finditer(r"\<[!&#\@]*[^<\@!&#]+[0-9]\>", message)
        matches = []
        matches = [x.group(0) for x in matches_re]
        if not len(matches):
            return message
        for match in matches:
            if server:
                if "#" in match:
                    mem = self.channelForName(match, server)
                elif "&" in match:
                    mem = self.roleForName(match, server)
                else:
                    mem = self.memberForName(match, server)
                if not mem:
                    continue
                mem_name = self.name(mem)
            else:
                memID = re.sub(r'\W+', '', match)
                mem = self.client.get_user(int(memID))
                if mem == None:
                    continue
                mem_name = mem.name
            message = message.replace(match, mem_name)
        return message

    def name(self, member : discord.Member):
        nick = name = None
        try:
            nick = member.nick
        except AttributeError:
            pass
        try:
            name = member.name
        except AttributeError:
            pass
        if nick:
            return Nullify.clean(nick)
        if name:
            return Nullify.clean(name)
        return None

    def memberForID(self, checkid, server):
        if server == None:
            mems = self.client.users
        else:
            mems = server.members
        try:
            checkid = int(checkid)
        except:
            return None
        for member in mems:
            if member.id == checkid:
                return member
        return None

    def memberForName(self, name, server):
        if server == None:
            mems = self.client.users
        else:
            mems = server.members
        name = str(name)
        for member in mems:
            if not hasattr(member,"nick"):
                break
            if member.nick:
                if member.nick.lower() == name.lower():
                    return member
        for member in mems:
            if member.name.lower() == name.lower():
                return member
        mem_parts = name.split("#")
        if len(mem_parts) == 2:
            try:
                mem_name = mem_parts[0]
                mem_disc = int(mem_parts[1])
            except:
                mem_name = mem_disc = None
            if mem_name:
                for member in mems:
                    if member.name.lower() == mem_name.lower() and int(member.discriminator) == mem_disc:
                        return member
        mem_id = re.sub(r'\W+', '', name)
        new_mem = self.memberForID(mem_id, server)
        if new_mem:
            return new_mem
        
        return None

    def channelForID(self, checkid, server, typeCheck = None):
        try:
            checkid = int(checkid)
        except:
            return None
        for channel in server.channels:
            if typeCheck:
                if typeCheck.lower() == "text" and not type(channel) is discord.TextChannel:
                    continue
                if typeCheck.lower() == "voice" and not type(channel) is discord.VoiceChannel:
                    continue
                if typeCheck.lower() == "category" and not type(channel) is discord.CategoryChannel:
                    continue
            if channel.id == checkid:
                return channel
        return None

    def channelForName(self, name, server, typeCheck = None):
        name = str(name)
        for channel in server.channels:
            if typeCheck:
                if typeCheck.lower() == "text" and not type(channel) is discord.TextChannel:
                    continue
                if typeCheck.lower() == "voice" and not type(channel) is discord.VoiceChannel:
                    continue
                if typeCheck.lower() == "category" and not type(channel) is discord.CategoryChannel:
                    continue
            if channel.name.lower() == name.lower():
                return channel
        chanID = re.sub(r'\W+', '', name)
        newChan = self.channelForID(chanID, server, typeCheck)
        if newChan:
            return newChan
        return None

    def roleForID(self, checkid, server):
        try:
            checkid = int(checkid)
        except:
            return None
        for role in server.roles:
            if role.id == checkid:
                return role
        return None

    def roleForName(self, name, server):
        name = str(name)
        if name.lower() == "everyone":
            name = "@everyone"
        for role in server.roles:
            if role.name.lower() == name.lower():
                return role
        roleID = ''.join(list(filter(str.isdigit, name)))
        newRole = self.roleForID(roleID, server)
        if newRole:
            return newRole
        return None

    def serverNick(self, user, server):
        for member in server.members:
            if member.id == user.id:
                return self.name(member)
        return None

    def checkNameForInt(self, name, server):
        name = str(name)
        theList = name.split()
        if len(theList)<2:
            amember = self.memberForName(name, server)
            if amember:
                return { "Member" : amember, "Int" : None }
            else:
                memID = ''.join(list(filter(str.isdigit, name)))
                newMem = self.memberForID(memID, server)
                if newMem:
                    return { "Member" : newMem, "Int" : None }
                else:
                    return { "Member" : None, "Int" : None }
        try:
            theInt = int(theList[len(theList)-1])
            newMemberName = " ".join(theList[:-1])
            amember = self.memberForName(newMemberName, server)
            if amember:
                return { "Member" : amember, "Int" : theInt }
            else:
                memID = ''.join(list(filter(str.isdigit, newMemberName)))
                newMem = self.memberForID(memID, server)
                if newMem:
                    return { "Member" : newMem, "Int" : theInt }
                else:
                    return { "Member" : None, "Int" : None }
        except ValueError:
            amember = self.memberForName(name, server)
            if amember:
                return { "Member" : amember, "Int" : None }
            else:
                memID = ''.join(list(filter(str.isdigit, name)))
                newMem = self.memberForID(memID, server)
                if newMem:
                    return { "Member" : newMem, "Int" : None }
                else:
                    return { "Member" : None, "Int" : None }
        return None

    def checkRoleForInt(self, name, server):
        name = str(name)
        theList = name.split()
        if len(theList)<2:
            amember = self.roleForName(name, server)
            if amember:
                return { "Role" : amember, "Int" : None }
            else:
                memID = ''.join(list(filter(str.isdigit, name)))
                newMem = self.roleForID(memID, server)
                if newMem:
                    return { "Role" : newMem, "Int" : None }
                else:
                    return { "Role" : None, "Int" : None }
        try:
            theInt = int(theList[len(theList)-1])
            newMemberName = " ".join(theList[:-1])
            amember = self.roleForName(newMemberName, server)
            if amember:
                return { "Role" : amember, "Int" : theInt }
            else:
                memID = ''.join(list(filter(str.isdigit, newMemberName)))
                newMem = self.roleForID(memID, server)
                if newMem:
                    return { "Role" : newMem, "Int" : theInt }
                else:
                    return { "Role" : None, "Int" : None }
        except ValueError:
            amember = self.roleForName(name, server)
            if amember:
                return { "Role" : amember, "Int" : None }
            else:
                memID = ''.join(list(filter(str.isdigit, name)))
                newMem = self.roleForID(memID, server)
                if newMem:
                    return { "Role" : newMem, "Int" : None }
                else:
                    return { "Role" : None, "Int" : None }
        return None
