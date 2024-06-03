import os
import random
import asyncio
import yt_dlp
from dotenv import load_dotenv
from youtubesearchpython import VideosSearch
import discord

def run_bot():
    load_dotenv()
    TOKEN = os.getenv('discord_token')
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    queues = {}
    voice_clients = {}
    yt_dl_options = {"format": "bestaudio/best"}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)

    ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}

    provocative_responses = [
        "Você acha mesmo que eu me importo?",
        "Essa pergunta é tão sem sentido que nem sei por onde começar...",
        "Já pensou em perguntar algo útil?",
        "Não estou com paciência para responder isso agora.",
        "Hahaha, boa piada... só que não.",
        "Não sei dizer. Talvez você devesse perguntar a um especialista em perguntas sem sentido.",
        "Sério mesmo que você está me perguntando isso?",
        "Acho que sua pergunta se perdeu no caminho para o bom senso.",
        "Pode parecer rude, mas essa é uma pergunta realmente inútil.",
        "Meu processador está tendo dificuldades para encontrar uma resposta para isso.",
        "Ah, claro, porque a minha preocupação com isso é tão grande quanto uma formiga no meio do oceano.",
        "Você espera uma resposta coerente para uma pergunta tão absurda? Boa sorte com isso.",
        "Se as perguntas sem sentido fossem dinheiro, você estaria nadando na riqueza agora.",
        "Parece que alguém ativou o modo aleatório nas perguntas hoje.",
        "Você realmente quer uma resposta ou só está praticando o seu monólogo de perguntas sem sentido?",
        "Acho que sua pergunta acabou de quebrar o meu medidor de ironia.",
        "Eu estava esperando uma pergunta inteligente, mas parece que fui premiado com isso.",
        "Se sua intenção era me deixar perplexo, parabéns, conseguiu.",
        "Acho que estou precisando de um upgrade de software para lidar com esse tipo de pergunta.",
        "Esta deve ser a pergunta mais surpreendente que já me fizeram... de tão inútil."
    ]
    
    used_responses = []  # Lista para armazenar as respostas já usadas

    async def play_next(guild_id):
        if guild_id in queues and queues[guild_id]:
            url = queues[guild_id].pop(0)
            data = await asyncio.get_event_loop().run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
            song = data['url']
            player = discord.FFmpegOpusAudio(song, **ffmpeg_options)
            voice_clients[guild_id].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(guild_id), client.loop).result())
        else:
            await voice_clients[guild_id].disconnect()
            del voice_clients[guild_id]

    @client.event
    async def on_ready():
        print(f'{client.user} is now jamming')
        for guild in client.guilds:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    await channel.send("Olá! Estou online. Por favor, digite `!help` para ver a lista de comandos disponíveis.")
                    break
            break  # Para enviar apenas uma vez por servidor

    @client.event
    async def on_message(message):
        if message.author == client.user:  
            return
        
        if message.content.startswith("!play"):
            try:
                voice_client = await message.author.voice.channel.connect()
                voice_clients[voice_client.guild.id] = voice_client
            except Exception as e:
                print(e)

            try:
                url = message.content.split()[1]

                if message.guild.id not in queues:
                    queues[message.guild.id] = []
                queues[message.guild.id].append(url)

                if not voice_clients[message.guild.id].is_playing():
                    await play_next(message.guild.id)
            except Exception as e:
                print(e)


        if message.content.startswith("!pause"):
            try:
                voice_clients[message.guild.id].pause()
            except Exception as e:
                print(e)

        if message.content.startswith("!resume"):
            try:
                voice_clients[message.guild.id].resume()
            except Exception as e:
                print(e)

        if message.content.startswith("!stop"):
            try:
                voice_clients[message.guild.id].stop()
                await voice_clients[message.guild.id].disconnect()
                del voice_clients[message.guild.id]
                del queues[message.guild.id]
            except Exception as e:
                print(e)

        if message.content.startswith("!skip"):
            try:
                voice_clients[message.guild.id].stop()
                await play_next(message.guild.id)
            except Exception as e:
                print(e)

        if message.content.startswith("!queue"):
            try:
                if message.guild.id in queues and queues[message.guild.id]:
                    queue_message = "**Fila de reprodução:**\n"
                    for index, url in enumerate(queues[message.guild.id], start=1):
                        queue_message += f"{index}. {url}\n"
                    await message.channel.send(queue_message)
                else:
                    await message.channel.send("Não há músicas na fila.")
            except Exception as e:
                print(e)

        if message.content.startswith("!help"):
            help_message = """
            **Comandos disponíveis:**
            - `!play <url>`: Adiciona uma música à fila de reprodução.
            - `!pause`: Pausa a reprodução da música atual.
            - `!resume`: Resume a reprodução da música pausada.
            - `!stop`: Para a reprodução da música atual e desconecta o bot do canal de voz.
            - `!skip`: Pula a música atual e reproduz a próxima na fila.
            - `!queue`: Mostra a fila de reprodução atual.
            - `!isaac`: Gera um número de 1 a 30 sobre quantos dias nosso amigo isaac não mente(tente também o nome de outros integrantes..).
            """
            await message.channel.send(help_message)

        if message.content.startswith("!isaac"):
            random_number = random.randint(1, 30)
            await message.channel.send(f'O número de dias que o isaac não mente é: {random_number}!')

        if message.content.startswith("!hillary"):
            random_number = random.randint(1, 30)
            await message.channel.send(f'O número de dias que a hillary não sofre com o trabalho são: {random_number}!')

        if message.content.startswith("!fellype"):
            random_number = random.randint(1, 300)
            await message.channel.send(f'O número de dias que fellype está sozinho em casa é exatos: {random_number}!')

        if message.content.startswith("!marcus"):
            random_number = random.randint(1, 350)
            await message.channel.send(f'O número de dias que marcus não trabalha na semana são: {random_number}!')

        if message.content.startswith("!davi"):
            random_number = random.randint(1, 2)
            await message.channel.send(f'O número de dias que davi parou de perguntar sobre o left for dead é: {random_number}!')

        if message.content.startswith("!eu"):
            random_number = random.randint(5, 20000)
            await message.channel.send(f'valor que você deve pra nubank: {random_number}!')

        if "?" in message.content:
            print("Mensagem recebida com interrogação")
            # Verifica se todas as respostas sarcásticas já foram usadas
            if len(used_responses) == len(provocative_responses):
                used_responses.clear()  # Limpa a lista de respostas usadas para recomeçar
            response = random.choice(list(set(provocative_responses) - set(used_responses)))  # Evita repetição
            used_responses.append(response)  # Adiciona a resposta usada à lista
            await message.channel.send(response)

    client.run(TOKEN)