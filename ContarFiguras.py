import sys

def Ler_imagem(caminho):
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
    return [[1-p for p in linha] for linha in im]

def dilatacao(imagem, mascara):
    altura = len(imagem)
    largura = len(imagem[0])
    
    nova_imagem = [[0 for _ in range(largura)] for _ in range(altura)] #Inicializa com zeros uma nova imagem para nao modificar a imagem original
    
    for y in range(1, altura - 1):
        for x in range(1, largura - 1):
            aplicar_dilatacao = False
            for j in range(-1, 2):
                for i in range(-1, 2):
                    if mascara[j + 1][i + 1] == 1 and imagem[y + j][x + i] == 1:
                        aplicar_dilatacao = True
            if aplicar_dilatacao:
                nova_imagem[y][x] = 1
            else:
                nova_imagem[y][x] = 0

    return nova_imagem

def envoltoria(imagem, imagem_dilatada):
    altura = len(imagem)
    largura = len(imagem[0])
    nova_imagem = [[0 for _ in range(largura)] for _ in range(altura)] #Inicializa com zeros uma nova imagem
    
    for y in range(altura):
        for x in range(largura):
            if imagem_dilatada[y][x] == 1 and imagem[y][x] == 0:
                nova_imagem[y][x] = 1
            else:
                nova_imagem[y][x] = 0

    return nova_imagem



def flood_fill_zero(imagem, x0, y0, mascara):

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
    altura = len(imagem)
    largura = len(imagem[0])
    copia = [linha[:] for linha in imagem]
    for y in range(altura):
        for x in range(largura):
            if imagem_buracos[y][x] == 1:
                copia[y][x] = 1
    return copia

def contar_figuras(imagem, mascara):
    contador = 0
    imagem_copia = [linha[:] for linha in imagem]
    for x in range(len(imagem[0])):
        for y in range(len(imagem)):
            if imagem_copia[y][x] == 1:
                flood_fill_zero(imagem_copia, x, y, mascara)
                contador += 1
    return contador


def main():
    if len(sys.argv) != 2:
        print("Número de argumentos inválido.")
        print("Uso: python ContarFiguras.py <caminho_para_imagem.pbm>")
        return
    
    caminho =  sys.argv[1]
    imagem, largura, altura = Ler_imagem(caminho)
    
    MASCARA =  [[1,1,1],
                [1,1,1],
                [1,1,1]]
    
    MASCARA_BURACO = [[0,1,0],
                      [1,1,1],
                      [0,1,0]]
    
    imagem_negativo = inverter(imagem)
    imagem_apenas_buracos = remover_fundo(imagem_negativo, MASCARA)
    imagam_sem_buracos = apaga_buracos(imagem, imagem_apenas_buracos)
    imagem_dilatada = dilatacao(imagam_sem_buracos, MASCARA)
    imagem_envoltoria = envoltoria(imagam_sem_buracos, imagem_dilatada)
    
    total_figuras = contar_figuras(imagem_envoltoria, MASCARA_BURACO)
    total_com_buracos = contar_figuras(imagem_apenas_buracos, MASCARA_BURACO)
    
    total_sem_buracos = total_figuras - total_com_buracos
    
    print(f"Total de figuras: {total_figuras}")
    print(f"Total de figuras COM buracos: {total_com_buracos}")
    print(f"Total de figuras SEM buracos: {total_sem_buracos}")
    
    
if __name__ == "__main__":
    main()
