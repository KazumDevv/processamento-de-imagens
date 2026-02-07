import sys

def Ler_imagem(caminho):
    """
    Lê um arquivo PBM no formato P1 (ASCII) e converte em uma matriz binária.

    Remove comentários e espaços extras, valida o cabeçalho do arquivo
    e garante que a quantidade de pixels corresponde às dimensões informadas.

    Args:
        caminho (str): Caminho para o arquivo PBM.

    Returns:
        tuple:
            matriz (list[list[int]]): Matriz 2D com valores 0 e 1.
            largura (int): Largura da imagem.
            altura (int): Altura da imagem.

    Raises:
        ValueError: Se o arquivo não for P1 válido ou estiver incompleto.
        FileNotFoundError: Se o arquivo não existir.
    """
    with open(caminho, "r") as arquivo:
        linhas = arquivo.readlines()

    tokens = []
    for linha in linhas:
        linha = linha.strip()
        
        if not linha or linha.startswith("#"):
            continue

        if "#" in linha:
            linha = linha.split("#")[0]

        tokens.extend(linha.split())

    if len(tokens) < 3:
        raise ValueError("arquivo PBM incompleto")

    if tokens[0] != "P1":
        raise ValueError("não é um arquivo PBM no formato P1")

    largura = int(tokens[1])
    altura = int(tokens[2])

    resto = "".join(tokens[3:])
    pixels = [int(c) for c in resto if c in "01"]

    if len(pixels) != largura * altura:
        raise ValueError(
            f"Pixels lidos: {len(pixels)} != esperado: {largura*altura}"
        )

    matriz = []
    i = 0
    for _ in range(altura):
        matriz.append(pixels[i:i+largura])
        i += largura

    return matriz, largura, altura

def inverter(im):
    """
    Gera o negativo de uma imagem binária.

    Troca todos os pixels 0 por 1 e 1 por 0.

    Args:
        im (list[list[int]]): Matriz binária da imagem.

    Returns:
        list[list[int]]: Nova matriz com valores invertidos.
    """

    return [[1-p for p in linha] for linha in im]

def erosao(imagem, mascara):
    """
    Aplica a operação morfológica de erosão em imagem binária.

    Um pixel permanece 1 somente se todos os pixels cobertos
    pela máscara forem 1 na imagem original.

    Args:
        imagem (list[list[int]]): Matriz binária de entrada.
        mascara (list[list[int]]): Elemento estruturante binário (ex: 3x3).

    Returns:
        list[list[int]]: Nova imagem erodida.
    """

    altura = len(imagem)
    largura = len(imagem[0])
    
    nova_imagem = [[0 for _ in range(largura)] for _ in range(altura)] #Inicializa com zeros uma nova imagem para nao modificar a imagem original
    
    for y in range(1, altura - 1):
        for x in range(1, largura - 1):
            aplicar_erosao = True
            for j in range(-1, 2):
                for i in range(-1, 2):
                    if mascara[j + 1][i + 1] == 1 and imagem[y + j][x + i] == 0:
                        aplicar_erosao = False
            if aplicar_erosao:
                nova_imagem[y][x] = 1
            else:
                nova_imagem[y][x] = 0

    return nova_imagem

def envoltoria(imagem, imagem_erodida):
    """
    Calcula a envoltória (contorno) dos objetos da imagem.

    Obtém os pixels que pertencem à imagem original mas foram removidos
    pela erosão — equivalente a borda morfológica.

    Args:
        imagem (list[list[int]]): Imagem binária original.
        imagem_erodida (list[list[int]]): Imagem após erosão.

    Returns:
        list[list[int]]: Imagem contendo apenas o contorno dos objetos.
    """

    altura = len(imagem)
    largura = len(imagem[0])
    nova_imagem = [[0 for _ in range(largura)] for _ in range(altura)] #Inicializa com zeros uma nova imagem
    
    for y in range(altura):
        for x in range(largura):
            if imagem_erodida[y][x] == 0 and imagem[y][x] == 1:
                nova_imagem[y][x] = 1
            else:
                nova_imagem[y][x] = 0

    return nova_imagem



def flood_fill_zero(imagem, x0, y0, mascara):
    """
    Executa flood fill apagando uma componente conectada.

    A partir de uma posição inicial, percorre todos os pixels conectados
    conforme a máscara de vizinhança e define seus valores como 0.

    Implementação iterativa usando pilha (DFS).

    Args:
        imagem (list[list[int]]): Matriz binária (modificada in-place).
        x0 (int): Coordenada x inicial.
        y0 (int): Coordenada y inicial.
        mascara (list[list[int]]): Máscara de conectividade (define vizinhos).

    Returns:
        None
    """

    altura = len(imagem)
    largura = len(imagem[0])

    altura_mascara = len(mascara)
    largura_mascara = len(mascara[0])

    centro_y = altura_mascara // 2
    centro_x = largura_mascara // 2

    pilha = [(x0, y0)]

    while pilha:
        x, y = pilha.pop()

        if x < 0 or y < 0 or x >= largura or y >= altura:
            continue

        if imagem[y][x] == 0:
            continue

        imagem[y][x] = 0

        for j in range(altura_mascara):
            for i in range(largura_mascara):

                if mascara[j][i] == 0:
                    continue

                deslocamento_x = i - centro_x
                deslocamento_y = j - centro_y

                if deslocamento_x == 0 and deslocamento_y == 0:
                    continue

                pilha.append((x + deslocamento_x, y + deslocamento_y))

def remover_fundo(im, mascara):
    """
    Remove o fundo conectado às bordas da imagem.

    Executa flood fill a partir das bordas para apagar regiões conectadas,
    útil para separar buracos internos de fundo externo.

    Args:
        im (list[list[int]]): Imagem binária.
        mascara (list[list[int]]): Máscara de conectividade.

    Returns:
        list[list[int]]: Nova imagem com o fundo removido.
    """

    altura = len(im)
    largura = len(im[0])

    copia = [linha[:] for linha in im]

    for x in range(largura):
        if copia[0][x] == 1:
            flood_fill_zero(copia, x, 0, mascara)
        if copia[altura-1][x] == 1:
            flood_fill_zero(copia, x, altura-1, mascara)

    for y in range(altura):
        if copia[y][0] == 1:
            flood_fill_zero(copia, 0, y, mascara)
        if copia[y][largura-1] == 1:
            flood_fill_zero(copia, largura-1, y, mascara)

    return copia

def apaga_buracos(imagem, imagem_buracos):
    """
    Preenche buracos internos em objetos binários.

    Combina a imagem original com a imagem de buracos detectados,
    marcando os pixels de buraco como pertencentes ao objeto.

    Args:
        imagem (list[list[int]]): Imagem original.
        imagem_buracos (list[list[int]]): Máscara dos buracos.

    Returns:
        list[list[int]]: Imagem com buracos preenchidos.
    """

    altura = len(imagem)
    largura = len(imagem[0])
    copia = [linha[:] for linha in imagem]
    for y in range(altura):
        for x in range(largura):
            if imagem_buracos[y][x] == 1:
                copia[y][x] = 1
    return copia

def contar_figuras(imagem, mascara):
    """
    Conta componentes conectados na imagem binária.

    Percorre a imagem e aplica flood fill em cada novo pixel 1 encontrado,
    incrementando o contador de objetos.

    Args:
        imagem (list[list[int]]): Imagem binária.
        mascara (list[list[int]]): Máscara de conectividade.

    Returns:
        int: Número de componentes conectados encontrados.
    """

    contador = 0
    imagem_copia = [linha[:] for linha in imagem]
    for x in range(len(imagem[0])):
        for y in range(len(imagem)):
            if imagem_copia[y][x] == 1:
                flood_fill_zero(imagem_copia, x, y, mascara)
                contador += 1
    return contador

def main():
    """
    Função principal do programa.

    Processa imagens PBM fornecidas via linha de comando,
    executa pipeline morfológico para:

    - inverter imagem
    - remover fundo
    - preencher buracos
    - calcular envoltória
    - contar figuras totais
    - contar figuras com e sem buracos

    Lê múltiplos arquivos passados como argumento.

    Returns:
        None
    """

    MASCARA =  [[1,1,1],
                [1,1,1],
                [1,1,1]]
    
    MASCARA_BURACO = [[0,1,0],
                      [1,1,1],
                      [0,1,0]]    
    
    if len(sys.argv) < 2:
        print("Número de argumentos inválido.")
        print("Uso: python ContarFiguras.py <caminho_para_imagem.pbm>")
        return

    for i in range(1, len(sys.argv)):
        caminho = sys.argv[i]
        
        try:
            imagem, largura, altura = Ler_imagem(caminho)
        except Exception as e:
            print(f"Erro ao ler o arquivo '{caminho}' ou não encontrado. Detalhes: {e}")
            return
        
        print(f'''Imagem lida: "{caminho}" (Largura: {largura}, Altura: {altura})''')
        print("Processando a imagem...")
        
        imagem_negativo = inverter(imagem)
        imagem_apenas_buracos = remover_fundo(imagem_negativo, MASCARA)
        imagam_sem_buracos = apaga_buracos(imagem, imagem_apenas_buracos)
        imagem_erodida = erosao(imagam_sem_buracos, MASCARA)
        imagem_envoltoria = envoltoria(imagam_sem_buracos, imagem_erodida)
        
        total_figuras = contar_figuras(imagem_envoltoria, MASCARA)
        total_com_buracos = contar_figuras(imagem_apenas_buracos, MASCARA_BURACO)
        
        total_sem_buracos = total_figuras - total_com_buracos
        
        print(f"Total de figuras: {total_figuras}")
        print(f"Total de figuras COM buracos: {total_com_buracos}")
        print(f"Total de figuras SEM buracos: {total_sem_buracos}")
        
    
if __name__ == "__main__":
    main()
