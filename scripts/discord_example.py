import discord  # noqa: INP001


class MyClient(discord.Client):
    async def on_ready(self) -> None:  # noqa: D102, ANN101
        for guild in client.guilds:
            for channel in guild.text_channels:
                with open(".env.bk", "a+") as f:  # noqa: ASYNC101, PTH123
                    f.write(
                        f'"{channel.name}": os.environ.get("{channel.name.upper()}_CID"),\n',  # noqa: E501
                    )
        print(f"Logged on as {self.user}!")  # noqa: T201

    async def on_message(self, message) -> None:  # noqa: ANN101, D102, ANN001
        print(f"Message from {message.author}: {message.content}")  # noqa: T201


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run("token")
