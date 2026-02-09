import discord
from discord.ext import commands
from discord import app_commands
import json
import os




# --- CONFIGURAÇÃO ---
TOKEN = "           " 
CANAL_MOD = 1459419271170887852  
CANAL_PP = 1405347166440132730   
CANAL_LOGS = 1461934924754980975 
ARQUIVO_PP = "pontos.json"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- SISTEMA DE ARQUIVOS (BANCO DE DADOS) ---
def carregar_pp():
    if not os.path.exists(ARQUIVO_PP):
        with open(ARQUIVO_PP, "w") as f:
            json.dump({}, f)
    with open(ARQUIVO_PP, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

def salvar_pp(dados):
    with open(ARQUIVO_PP, "w") as f:
        json.dump(dados, f, indent=4)

def adicionar_pontos(user_id, pontos):
    dados = carregar_pp()
    user_id_str = str(user_id)
    dados[user_id_str] = dados.get(user_id_str, 0) + pontos
    salvar_pp(dados)

# --- PAINEL DE MODERAÇÃO (BOTÕES) ---
class PainelModeracao(discord.ui.View):
    def __init__(self, autor, descricao, midia):
        super().__init__(timeout=None)
        self.autor = autor
        self.descricao = descricao
        self.midia = midia

    @discord.ui.button(label="Aprovar", style=discord.ButtonStyle.green, custom_id="btn_aprovar_pp")
    async def aprovar(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        view_origem = self

        class ModalPontos(discord.ui.Modal, title="Atribuir Pontos Policiais"):
            qtd = discord.ui.TextInput(label="Quantidade de PP", placeholder="Ex: 10", min_length=1)

            async def on_submit(self, modal_inter: discord.Interaction):
                try:
                    valor = int(self.qtd.value)
                except ValueError:
                    return await modal_inter.response.send_message("Use apenas números!", ephemeral=True)

                adicionar_pontos(view_origem.autor.id, valor)
                canal_publico = bot.get_channel(CANAL_PP)

                embed = discord.Embed(
                    title="✅ Solicitação Aprovada!",
                    description=f"O oficial {view_origem.autor.mention} recebeu **{valor} PP**!",
                    color=0x00FF00
                )
                embed.add_field(name="Motivo:", value=view_origem.descricao)

                if view_origem.midia.content_type and view_origem.midia.content_type.startswith("image/"):
                    embed.set_image(url=view_origem.midia.url)
                    await canal_publico.send(content=view_origem.autor.mention, embed=embed)
                else:
                    await canal_publico.send(content=f"✅ {view_origem.autor.mention} recebeu **{valor} PP**!\n{view_origem.midia.url}", embed=embed)

                await modal_inter.response.send_message(f"Pontos aplicados com sucesso!", ephemeral=True)
                await interaction.edit_original_response(view=None) # Remove os botões

        await interaction.response.send_modal(ModalPontos())

    @discord.ui.button(label="Recusar", style=discord.ButtonStyle.red, custom_id="btn_recusar_pp")
    async def recusar(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await self.autor.send(f"❌ Sua solicitação de PP foi recusada pela moderação.\n**Motivo:** {self.descricao}")
        except:
            pass
        await interaction.response.send_message("Solicitação recusada.", ephemeral=True)
        await interaction.message.delete()

# --- COMANDOS SLASH ---

@bot.tree.command(name="enviar", description="Envia prova para ganhar PP.")
async def enviar(interaction: discord.Interaction, descricao: str, midia: discord.Attachment):
    await interaction.response.defer(ephemeral=True)

    if not midia.content_type or not (midia.content_type.startswith("image/") or midia.content_type.startswith("video/")):
        return await interaction.followup.send("Envie apenas fotos ou vídeos!", ephemeral=True)

    canal_analise = bot.get_channel(CANAL_MOD)
    if not canal_analise:
        return await interaction.followup.send("Erro: Canal de moderação não encontrado.", ephemeral=True)

    view = PainelModeracao(interaction.user, descricao, midia)
    
    embed_staff = discord.Embed(
        title="👮 Nova Prova Enviada",
        description=f"**Oficial:** {interaction.user.mention}\n**Descrição:** {descricao}",
        color=0x0000FF
    )

    if midia.content_type.startswith("image/"):
        embed_staff.set_image(url=midia.url)
        await canal_analise.send(embed=embed_staff, view=view)
    else:
        await canal_analise.send(content=f"🎥 **VÍDEO DE:** {interaction.user.mention}\n{midia.url}", embed=embed_staff, view=view)

    await interaction.followup.send("Sua prova foi enviada para análise da Staff!", ephemeral=True)

@bot.tree.command(name="ranking", description="Mostra o TOP 10 Oficiais.")
async def ranking(interaction: discord.Interaction):
    dados = carregar_pp()
    if not dados:
        return await interaction.response.send_message("Ninguém possui pontos ainda.")

    ranking_ordenado = sorted(dados.items(), key=lambda x: x[1], reverse=True)[:10]
    embed = discord.Embed(title="🏆 Ranking de Pontos Policiais", color=0xFFD700)
    
    lista = ""
    for i, (user_id, pontos) in enumerate(ranking_ordenado, start=1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🔹"
        lista += f"{emoji} **{i}º** <@{user_id}> — `{pontos} PP`\n"

    embed.description = lista
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="perfil", description="Vê os teus próprios pontos.")
async def perfil(interaction: discord.Interaction, usuario: discord.Member = None):
    alvo = usuario or interaction.user
    dados = carregar_pp()
    pts = dados.get(str(alvo.id), 0)
    await interaction.response.send_message(f"📊 {alvo.mention} possui atualmente **{pts} PP**.", ephemeral=True)

@bot.tree.command(name="setpp", description="[STAFF] Define pontos de um usuário.")
@app_commands.checks.has_permissions(manage_roles=True)
async def setpp(interaction: discord.Interaction, usuario: discord.Member, quantidade: int):
    dados = carregar_pp()
    dados[str(usuario.id)] = quantidade
    salvar_pp(dados)
    await interaction.response.send_message(f"✅ Pontos de {usuario.mention} definidos para **{quantidade}**.", ephemeral=True)
# --- COMANDO DE ANÚNCIO (VERSÃO BLINDADA) ---
@bot.tree.command(name="anunciar", description="[STAFF] Cria um anúncio completo.")
@app_commands.checks.has_permissions(manage_messages=True)
async def anunciar(interaction: discord.Interaction, canal: discord.TextChannel):
    # Avisamos o Discord IMEDIATAMENTE que recebemos o comando
    # Isso mata o erro 10062 (Unknown Interaction)
    
    class ModalFinal(discord.ui.Modal, title="Etapa Final: Conteúdo"):
        desc = discord.ui.TextInput(label="Descrição", style=discord.TextStyle.paragraph, placeholder="Texto principal...", required=True)
        rodape = discord.ui.TextInput(label="Rodapé", placeholder="Texto lá embaixo...", required=False)
        btn_txt = discord.ui.TextInput(label="Botão: Texto", placeholder="Ex: Site", required=False)
        btn_url = discord.ui.TextInput(label="Botão: Link", placeholder="https://...", required=False)

        def __init__(self, d1):
            super().__init__()
            self.d1 = d1

        async def on_submit(self, it_final: discord.Interaction):
            await it_final.response.defer(ephemeral=True)
            try:
                cor = int(self.d1['cor'].replace("#", ""), 16)
            except:
                cor = discord.Color.blue().value

            embed = discord.Embed(title=self.d1['titulo'], description=self.desc.value, color=cor)
            if self.d1['autor']: embed.set_author(name=self.d1['autor'])
            
            # Verificação básica de links para evitar Erro 500
            if self.d1['thumb'] and self.d1['thumb'].startswith("http"): embed.set_thumbnail(url=self.d1['thumb'])
            if self.d1['img'] and self.d1['img'].startswith("http"): embed.set_image(url=self.d1['img'])
            if self.rodape.value: embed.set_footer(text=self.rodape.value)

            view = None
            if self.btn_txt.value and self.btn_url.value.startswith("http"):
                view = discord.ui.View()
                view.add_item(discord.ui.Button(label=self.btn_txt.value, url=self.btn_url.value))

            await canal.send(embed=embed, view=view)
            await it_final.followup.send("✅ Enviado!", ephemeral=True)

    class ModalInicio(discord.ui.Modal, title="Etapa 1: Visual"):
        titulo = discord.ui.TextInput(label="Título", required=True)    
        autor = discord.ui.TextInput(label="Autor", required=False)
        thumb = discord.ui.TextInput(label="Thumbnail (Link)", required=False)
        img = discord.ui.TextInput(label="Imagem Grande (Link)", required=False)
        cor = discord.ui.TextInput(label="Cor Hex", default="#10BF07A9", required=False)

        async def on_submit(self, it_inicio: discord.Interaction):
            dados = {
                'titulo': self.titulo.value, 'autor': self.autor.value,
                'thumb': self.thumb.value, 'img': self.img.value, 'cor': self.cor.value
            }
            # Botão de ponte para a etapa 2
            view = discord.ui.View()
            btn = discord.ui.Button(label="Próximo Passo", style=discord.ButtonStyle.green)
            async def ir_p2(it_btn: discord.Interaction):
                await it_btn.response.send_modal(ModalFinal(dados))
            btn.callback = ir_p2
            view.add_item(btn)
            await it_inicio.response.send_message("Configuração visual salva! Clique abaixo:", view=view, ephemeral=True)

    # O truque está aqui: enviamos o primeiro modal direto na resposta do comando

    await interaction.response.send_modal(ModalInicio())
    
    # --- INICIALIZAÇÃO ---
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"[+] Bot Online: {bot.user}")
    print(f"[+] Comandos Sincronizados")
bot.run(TOKEN)  





                