import cv2
import numpy as np
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk

# Variáveis globais
captura = None  # Variável para armazenar a captura de vídeo
tipo_filtro = None  # Tipo de filtro aplicado ao vídeo ou imagem
brilho = 1.0  # Nível de brilho inicial
contraste = 1.0  # Nível de contraste inicial
modo_imagem = False  # Define se está no modo de imagem (parado) ou vídeo (tempo real)
fotograma_capturado = None  # Armazena o fotograma capturado quando em modo de imagem

# Função para iniciar a captura de vídeo
def iniciar_video():
    """
    Inicia a captura de vídeo da câmara e chama a função para processar o vídeo em tempo real.
    """
    global captura
    captura = cv2.VideoCapture(0)  # Ativa a câmara principal do dispositivo
    processar_video()

# Função para processar o vídeo em tempo real
def processar_video():
    """
    Processa os fotogramas do vídeo capturado e aplica os filtros definidos.
    """
    global captura, tipo_filtro, brilho, contraste, modo_imagem, fotograma_capturado
    if not modo_imagem:  # Apenas processa o vídeo se não estiver no modo de imagem
        ret, fotograma = captura.read()  # Lê um fotograma da câmara
        if ret:  # Verifica se o fotograma foi capturado com sucesso
            fotograma = aplicar_filtros(fotograma)  # Aplica os filtros ao fotograma
            exibir_fotograma(fotograma)  # Exibe o fotograma processado na interface
    raiz.after(10, processar_video)  # Agenda a próxima chamada da função

# Função para aplicar filtros ao fotograma
def aplicar_filtros(fotograma):
    """
    Aplica os filtros selecionados e ajusta brilho e contraste ao fotograma.
    """
    global tipo_filtro, brilho, contraste

    # Ajuste de brilho e contraste
    fotograma = cv2.convertScaleAbs(fotograma, alpha=contraste, beta=int(brilho * 50))

    # Aplica o filtro selecionado
    if tipo_filtro == "cinzento":
        fotograma = cv2.cvtColor(fotograma, cv2.COLOR_BGR2GRAY)  # Converte para escala de cinza
    elif tipo_filtro == "bordas":
        fotograma = cv2.Canny(fotograma, 50, 150)  # Aplica deteção de bordas (Canny)
    elif tipo_filtro == "desfocar":
        fotograma = cv2.GaussianBlur(fotograma, (15, 15), 0)  # Aplica um desfoque Gaussian
    elif tipo_filtro == "sepia":
        # Aplica o efeito sépia utilizando uma matriz de transformação
        matriz = np.array([[0.272, 0.534, 0.131],
                           [0.349, 0.686, 0.168],
                           [0.393, 0.769, 0.189]])
        fotograma = cv2.transform(fotograma, matriz)
        fotograma = np.clip(fotograma, 0, 255).astype(np.uint8)

    return fotograma

# Função para capturar uma imagem estática
def capturar_imagem():
    """
    Captura o fotograma atual da câmara e aplica os filtros selecionados.
    """
    global fotograma_capturado, modo_imagem
    modo_imagem = True  # Ativa o modo de imagem (pausa o vídeo)
    ret, fotograma = captura.read()  # Lê o fotograma atual da câmara
    if ret:  # Verifica se o fotograma foi capturado com sucesso
        fotograma_capturado = aplicar_filtros(fotograma)  # Aplica os filtros ao fotograma capturado
        exibir_fotograma(fotograma_capturado)  # Exibe o fotograma capturado na interface

# Função para exibir um fotograma na interface
def exibir_fotograma(fotograma):
    """
    Converte o fotograma para o formato apropriado e exibe-o na interface gráfica.
    """
    if len(fotograma.shape) == 2:  # Verifica se o fotograma está em escala de cinza
        fotograma = cv2.cvtColor(fotograma, cv2.COLOR_GRAY2RGB)  # Converte para RGB
    else:
        fotograma = cv2.cvtColor(fotograma, cv2.COLOR_BGR2RGB)  # Converte de BGR para RGB

    imagem = Image.fromarray(fotograma)  # Converte o fotograma num objeto PIL Image
    imagem_tk = ImageTk.PhotoImage(image=imagem)  # Converte para um formato compatível com Tkinter
    etiqueta_video.imgtk = imagem_tk
    etiqueta_video.configure(image=imagem_tk)  # Atualiza a imagem exibida na interface

# Função para salvar a imagem processada
def salvar_imagem():
    """
    Permite ao utilizador salvar a imagem capturada com os filtros aplicados.
    """
    global fotograma_capturado
    if fotograma_capturado is not None:  # Verifica se existe uma imagem capturada
        caminho_ficheiro = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                        filetypes=[("Ficheiros JPEG", "*.jpg"),
                                                                   ("Ficheiros PNG", "*.png")])
        if caminho_ficheiro:  # Verifica se foi selecionado um caminho válido
            # Salva a imagem no formato BGR (usado pelo OpenCV)
            cv2.imwrite(caminho_ficheiro, cv2.cvtColor(fotograma_capturado, cv2.COLOR_RGB2BGR))
            print("Imagem salva em:", caminho_ficheiro)

# Função para contar objetos na imagem capturada
def contar_objetos():
    """
    Conta o número de objetos identificáveis na imagem capturada.
    """
    global fotograma_capturado
    if fotograma_capturado is not None:  # Verifica se existe uma imagem capturada
        # Converte para escala de cinza e aplica desfoque para suavizar
        cinzento = cv2.cvtColor(fotograma_capturado, cv2.COLOR_BGR2GRAY)
        desfocado = cv2.GaussianBlur(cinzento, (5, 5), 0)
        _, binario = cv2.threshold(desfocado, 128, 255, cv2.THRESH_BINARY)  # Binariza a imagem
        contornos, _ = cv2.findContours(binario, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Desenha os contornos na imagem e exibe o resultado
        fotograma_resultado = fotograma_capturado.copy()
        for contorno in contornos:
            cv2.drawContours(fotograma_resultado, [contorno], -1, (0, 255, 0), 2)
        exibir_fotograma(fotograma_resultado)
        print("Objetos detectados:", len(contornos))

# Funções para alterar filtros
def definir_filtro_cinzento():
    global tipo_filtro
    tipo_filtro = "cinzento"  # Define o filtro como escala de cinza

def definir_filtro_bordas():
    global tipo_filtro
    tipo_filtro = "bordas"  # Define o filtro como deteção de bordas

def definir_filtro_desfocar():
    global tipo_filtro
    tipo_filtro = "desfocar"  # Define o filtro como desfoque

def definir_filtro_sepia():
    global tipo_filtro
    tipo_filtro = "sepia"  # Define o filtro como sépia

def resetar_filtros():
    global tipo_filtro
    tipo_filtro = None  # Remove todos os filtros

# Funções para ajustar brilho e contraste
def ajustar_brilho(valor):
    global brilho
    brilho = float(valor)  # Atualiza o valor do brilho

def ajustar_contraste(valor):
    global contraste
    contraste = float(valor)  # Atualiza o valor do contraste

# Configuração da interface gráfica
raiz = Tk()
raiz.title("Processamento de Imagem com OpenCV")
raiz.geometry("800x600")

# Exibição de vídeo
etiqueta_video = Label(raiz)
etiqueta_video.pack()

# Botões de controlo
frame_botoes = Frame(raiz)
frame_botoes.pack()

Button(frame_botoes, text="Iniciar Vídeo", command=iniciar_video).grid(row=0, column=0)
Button(frame_botoes, text="Capturar Imagem", command=capturar_imagem).grid(row=0, column=1)
Button(frame_botoes, text="Salvar Imagem", command=salvar_imagem).grid(row=0, column=2)
Button(frame_botoes, text="Contar Objetos", command=contar_objetos).grid(row=0, column=3)

# Botões de filtros
frame_filtros = Frame(raiz)
frame_filtros.pack()

Button(frame_filtros, text="Escala de Cinzento", command=definir_filtro_cinzento).grid(row=0, column=0)
Button(frame_filtros, text="Deteção de Bordas", command=definir_filtro_bordas).grid(row=0, column=1)
Button(frame_filtros, text="Desfocar", command=definir_filtro_desfocar).grid(row=0, column=2)
Button(frame_filtros, text="Efeito Sépia", command=definir_filtro_sepia).grid(row=0, column=3)
Button(frame_filtros, text="Resetar Filtros", command=resetar_filtros).grid(row=0, column=4)

# Sliders para ajuste de brilho e contraste
frame_sliders = Frame(raiz)
frame_sliders.pack()

Label(frame_sliders, text="Brilho").grid(row=0, column=0)
slider_brilho = Scale(frame_sliders, from_=0.0, to=2.0, resolution=0.1,
                      orient=HORIZONTAL, command=ajustar_brilho)
slider_brilho.set(1.0)  # Define o valor inicial do brilho
slider_brilho.grid(row=0, column=1)

Label(frame_sliders, text="Contraste").grid(row=1, column=0)
slider_contraste = Scale(frame_sliders, from_=0.0, to=2.0, resolution=0.1,
                         orient=HORIZONTAL, command=ajustar_contraste)
slider_contraste.set(1.0)  # Define o valor inicial do contraste
slider_contraste.grid(row=1, column=1)

# Inicia o loop da interface
raiz.mainloop()